from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import pymysql
import pandas as pd
from data_ingestion.models import DataSource

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_mysql_connection(request):
    connection_details = request.data
    
    try:
        conn = pymysql.connect(
            host=connection_details.get('host'),
            port=int(connection_details.get('port', 3306)),
            user=connection_details.get('user'),
            password=connection_details.get('password'),
            database=connection_details.get('database'),
        )
        
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        conn.close()
        
        return Response({
            'success': True,
            'message': 'Connection successful',
            'tables': tables
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Connection failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_data_source(request):
    try:
        data_source = DataSource.objects.create(
            user=request.user,
            name=request.data.get('name'),
            source_type=request.data.get('source_type'),
            connection_details=request.data.get('connection_details', {})
        )
        
        return Response({
            'id': str(data_source.id),
            'name': data_source.name,
            'source_type': data_source.source_type,
            'created_at': data_source.created_at
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_data_sources(request):
    sources = DataSource.objects.filter(user=request.user, is_active=True)
    
    return Response({
        'data_sources': [{
            'id': str(s.id),
            'name': s.name,
            'source_type': s.source_type,
            'created_at': s.created_at
        } for s in sources]
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_from_mysql(request, source_id):
    table_name = request.data.get('table')
    query = request.data.get('query')
    
    try:
        source = DataSource.objects.get(id=source_id, user=request.user)
        
        if source.source_type != 'mysql':
            return Response({'detail': 'Not a MySQL data source'}, status=status.HTTP_400_BAD_REQUEST)
        
        details = source.connection_details
        conn = pymysql.connect(
            host=details.get('host'),
            port=int(details.get('port', 3306)),
            user=details.get('user'),
            password=details.get('password'),
            database=details.get('database'),
        )
        
        if query:
            df = pd.read_sql(query, conn)
        elif table_name:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        else:
            return Response({'detail': 'Provide either table or query'}, status=status.HTTP_400_BAD_REQUEST)
        
        conn.close()
        
        return Response({
            'success': True,
            'rows': len(df),
            'columns': df.columns.tolist(),
            'preview': df.head(10).to_dict('records')
        })
    
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
