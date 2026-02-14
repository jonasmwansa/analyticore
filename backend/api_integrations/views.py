from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import redirect
from django.conf import settings
import pymysql
import psycopg2
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timezone, timedelta
from data_ingestion.models import DataSource
from .models import GoogleSheetsToken
from . import google_sheets as gs

logger = logging.getLogger(__name__)


def convert_to_serializable(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(v) for v in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj) if not np.isnan(obj) else None
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif pd.isna(obj):
        return None
    return obj


# ==================== MySQL Integration ====================

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


# ==================== PostgreSQL Integration ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_postgresql_connection(request):
    """Test PostgreSQL database connection"""
    connection_details = request.data
    
    try:
        conn = psycopg2.connect(
            host=connection_details.get('host'),
            port=int(connection_details.get('port', 5432)),
            user=connection_details.get('user'),
            password=connection_details.get('password'),
            database=connection_details.get('database'),
        )
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' ORDER BY table_name
        """)
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


# ==================== Data Sources CRUD ====================

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


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_data_source(request, source_id):
    try:
        source = DataSource.objects.get(id=source_id, user=request.user)
        source.is_active = False
        source.save()
        return Response({'message': 'Data source deleted'})
    except DataSource.DoesNotExist:
        return Response({'detail': 'Data source not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== Import from Database ====================

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
            df = pd.read_sql(f"SELECT * FROM `{table_name}`", conn)
        else:
            return Response({'detail': 'Provide either table or query'}, status=status.HTTP_400_BAD_REQUEST)
        
        conn.close()
        
        preview_data = convert_to_serializable(df.head(10).to_dict('records'))
        
        return Response({
            'success': True,
            'rows': len(df),
            'columns': df.columns.tolist(),
            'preview': preview_data
        })
    
    except DataSource.DoesNotExist:
        return Response({'detail': 'Data source not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_from_postgresql(request, source_id):
    """Import data from PostgreSQL"""
    table_name = request.data.get('table')
    query = request.data.get('query')
    
    try:
        source = DataSource.objects.get(id=source_id, user=request.user)
        
        if source.source_type != 'postgresql':
            return Response({'detail': 'Not a PostgreSQL data source'}, status=status.HTTP_400_BAD_REQUEST)
        
        details = source.connection_details
        conn = psycopg2.connect(
            host=details.get('host'),
            port=int(details.get('port', 5432)),
            user=details.get('user'),
            password=details.get('password'),
            database=details.get('database'),
        )
        
        if query:
            df = pd.read_sql(query, conn)
        elif table_name:
            df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        else:
            return Response({'detail': 'Provide either table or query'}, status=status.HTTP_400_BAD_REQUEST)
        
        conn.close()
        
        preview_data = convert_to_serializable(df.head(10).to_dict('records'))
        
        return Response({
            'success': True,
            'rows': len(df),
            'columns': df.columns.tolist(),
            'preview': preview_data
        })
    
    except DataSource.DoesNotExist:
        return Response({'detail': 'Data source not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== Google Sheets Integration ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_sheets_status(request):
    """Check if user has connected Google Sheets"""
    try:
        token = GoogleSheetsToken.objects.get(user=request.user)
        
        # Check if credentials are configured
        if not os.environ.get('GOOGLE_SHEETS_CLIENT_ID'):
            return Response({
                'connected': False,
                'configured': False,
                'message': 'Google Sheets integration not configured'
            })
        
        return Response({
            'connected': True,
            'configured': True,
            'email': token.google_email,
            'connected_at': token.created_at
        })
    except GoogleSheetsToken.DoesNotExist:
        configured = bool(os.environ.get('GOOGLE_SHEETS_CLIENT_ID'))
        return Response({
            'connected': False,
            'configured': configured,
            'message': 'Not connected to Google Sheets' if configured else 'Google Sheets integration not configured'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_sheets_auth_url(request):
    """Get Google OAuth authorization URL"""
    try:
        if not os.environ.get('GOOGLE_SHEETS_CLIENT_ID'):
            return Response({
                'error': 'Google Sheets integration not configured. Please add GOOGLE_SHEETS_CLIENT_ID and GOOGLE_SHEETS_CLIENT_SECRET to your environment.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        auth_url, state = gs.get_authorization_url(request.user.id)
        
        return Response({
            'auth_url': auth_url,
            'state': state
        })
    except Exception as e:
        logger.error(f"Error generating auth URL: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def google_sheets_callback(request):
    """Handle Google OAuth callback"""
    code = request.GET.get('code')
    state = request.GET.get('state')  # Contains user_id
    error = request.GET.get('error')
    
    frontend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://insights-dashboard-18.preview.emergentagent.com')
    
    if error:
        return redirect(f"{frontend_url}/dashboard?sheets_error={error}")
    
    if not code or not state:
        return redirect(f"{frontend_url}/dashboard?sheets_error=missing_params")
    
    try:
        # Exchange code for tokens
        creds = gs.exchange_code_for_tokens(code, state)
        
        # Get user from state
        from users.models import User
        user = User.objects.get(id=state)
        
        # Calculate expiry
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=creds.expiry.timestamp() - datetime.now().timestamp()) if creds.expiry else datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Get user email from token
        from googleapiclient.discovery import build
        oauth2_service = build('oauth2', 'v2', credentials=creds)
        user_info = oauth2_service.userinfo().get().execute()
        google_email = user_info.get('email')
        
        # Save or update token
        GoogleSheetsToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token': creds.token,
                'refresh_token': creds.refresh_token,
                'expires_at': expires_at,
                'scopes': list(creds.scopes) if creds.scopes else [],
                'google_email': google_email
            }
        )
        
        return redirect(f"{frontend_url}/dashboard?sheets_connected=true")
    
    except User.DoesNotExist:
        return redirect(f"{frontend_url}/signin?sheets_error=invalid_user")
    except Exception as e:
        logger.error(f"Google Sheets callback error: {str(e)}")
        return redirect(f"{frontend_url}/dashboard?sheets_error={str(e)[:100]}")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def google_sheets_disconnect(request):
    """Disconnect Google Sheets (revoke token)"""
    try:
        token = GoogleSheetsToken.objects.get(user=request.user)
        
        # Revoke token
        gs.revoke_token(token.to_dict())
        
        # Delete from database
        token.delete()
        
        return Response({'message': 'Google Sheets disconnected successfully'})
    except GoogleSheetsToken.DoesNotExist:
        return Response({'message': 'Not connected to Google Sheets'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_sheets_list(request):
    """List user's Google Sheets"""
    try:
        token = GoogleSheetsToken.objects.get(user=request.user)
        
        spreadsheets = gs.list_spreadsheets(token.to_dict())
        
        return Response({
            'spreadsheets': spreadsheets
        })
    except GoogleSheetsToken.DoesNotExist:
        return Response({'error': 'Not connected to Google Sheets'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error listing spreadsheets: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_sheets_metadata(request, spreadsheet_id):
    """Get spreadsheet metadata including sheets"""
    try:
        token = GoogleSheetsToken.objects.get(user=request.user)
        
        metadata = gs.get_spreadsheet_metadata(token.to_dict(), spreadsheet_id)
        
        return Response(metadata)
    except GoogleSheetsToken.DoesNotExist:
        return Response({'error': 'Not connected to Google Sheets'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error getting spreadsheet metadata: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def google_sheets_preview(request, spreadsheet_id):
    """Preview data from a Google Sheet"""
    sheet_name = request.data.get('sheet_name')
    range_notation = request.data.get('range')
    
    try:
        token = GoogleSheetsToken.objects.get(user=request.user)
        
        headers, data = gs.read_sheet_data(
            token.to_dict(),
            spreadsheet_id,
            sheet_name=sheet_name,
            range_notation=range_notation
        )
        
        # Convert to preview format (first 20 rows)
        preview_data = []
        for row in data[:20]:
            record = {headers[i]: row[i] if i < len(row) else '' for i in range(len(headers))}
            preview_data.append(record)
        
        return Response({
            'columns': headers,
            'data': preview_data,
            'total_rows': len(data)
        })
    except GoogleSheetsToken.DoesNotExist:
        return Response({'error': 'Not connected to Google Sheets'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error previewing sheet: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def google_sheets_import(request, project_id):
    """Import Google Sheets data into a project"""
    from projects.models import Project
    from pipelines.context import PipelineContext
    from pipelines.base import Pipeline
    from pipelines.steps import ColumnUnderstandingStep
    
    spreadsheet_id = request.data.get('spreadsheet_id')
    sheet_name = request.data.get('sheet_name')
    range_notation = request.data.get('range')
    
    if not spreadsheet_id:
        return Response({'error': 'spreadsheet_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verify project belongs to user
        project = Project.objects.get(project_id=project_id, user=request.user)
        
        # Get token
        token = GoogleSheetsToken.objects.get(user=request.user)
        
        # Read sheet data
        headers, data = gs.read_sheet_data(
            token.to_dict(),
            spreadsheet_id,
            sheet_name=sheet_name,
            range_notation=range_notation
        )
        
        if not headers:
            return Response({'error': 'No data found in the sheet'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=headers)
        
        # Save to file
        file_path = os.path.join(settings.PIPELINE_STORAGE_PATH, 'original', f"{project_id}_google_sheets.csv")
        df.to_csv(file_path, index=False)
        
        # Run column understanding pipeline
        context = PipelineContext(
            project_id=str(project_id),
            original_df=df.copy(),
            current_df=df.copy()
        )
        
        pipeline = Pipeline("Column Understanding")
        pipeline.add_step(ColumnUnderstandingStep())
        context = pipeline.execute(context)
        
        # Build statistics
        def convert_value(obj):
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj) if not np.isnan(obj) else None
            elif pd.isna(obj):
                return None
            return obj
        
        statistics = {
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'columns': df.columns.tolist(),
            'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'missing_values': {col: int(v) for col, v in df.isnull().sum().items()},
            'sample_data': [{k: convert_value(v) for k, v in row.items()} for row in df.head(5).to_dict('records')],
            'column_metadata': {name: {
                'inferred_type': meta.inferred_type,
                'confidence': float(meta.confidence),
                'missing_percentage': float(meta.missing_percentage),
                'unique_count': int(meta.unique_count),
                'is_identifier': bool(meta.is_identifier),
                'statistics': {k: convert_value(v) for k, v in meta.statistics.items()} if meta.statistics else {}
            } for name, meta in context.metadata.items()}
        }
        
        # Get spreadsheet title for the filename
        metadata = gs.get_spreadsheet_metadata(token.to_dict(), spreadsheet_id)
        sheet_title = sheet_name or 'Sheet1'
        
        # Update project
        project.original_filename = f"{metadata['title']} - {sheet_title}.csv"
        project.file_path = file_path
        project.row_count = len(df)
        project.column_count = len(df.columns)
        project.status = 'uploaded'
        project.statistics = statistics
        project.save()
        
        return Response({
            'message': 'Data imported successfully from Google Sheets',
            'statistics': statistics
        })
    
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    except GoogleSheetsToken.DoesNotExist:
        return Response({'error': 'Not connected to Google Sheets'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error importing from Google Sheets: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== Direct Database Import to Project ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_database_to_project(request, project_id):
    """Import data from MySQL or PostgreSQL directly into a project"""
    from projects.models import Project
    from pipelines.context import PipelineContext
    from pipelines.base import Pipeline
    from pipelines.steps import ColumnUnderstandingStep
    
    db_type = request.data.get('db_type')  # 'mysql' or 'postgresql'
    host = request.data.get('host')
    port = request.data.get('port')
    database = request.data.get('database')
    user = request.data.get('user')
    password = request.data.get('password')
    table_name = request.data.get('table')
    query = request.data.get('query')
    
    if not db_type or not host or not database or not user:
        return Response({'error': 'Missing required connection parameters'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not table_name and not query:
        return Response({'error': 'Provide either table or query'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verify project belongs to user
        project = Project.objects.get(project_id=project_id, user=request.user)
        
        # Connect and fetch data
        if db_type == 'mysql':
            conn = pymysql.connect(
                host=host,
                port=int(port or 3306),
                user=user,
                password=password or '',
                database=database,
            )
            if query:
                df = pd.read_sql(query, conn)
            else:
                df = pd.read_sql(f"SELECT * FROM `{table_name}`", conn)
        elif db_type == 'postgresql':
            conn = psycopg2.connect(
                host=host,
                port=int(port or 5432),
                user=user,
                password=password or '',
                database=database,
            )
            if query:
                df = pd.read_sql(query, conn)
            else:
                df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        else:
            return Response({'error': 'Invalid database type'}, status=status.HTTP_400_BAD_REQUEST)
        
        conn.close()
        
        # Save to file
        source_name = table_name or 'query_result'
        file_path = os.path.join(settings.PIPELINE_STORAGE_PATH, 'original', f"{project_id}_{db_type}_{source_name}.csv")
        df.to_csv(file_path, index=False)
        
        # Run column understanding pipeline
        context = PipelineContext(
            project_id=str(project_id),
            original_df=df.copy(),
            current_df=df.copy()
        )
        
        pipeline = Pipeline("Column Understanding")
        pipeline.add_step(ColumnUnderstandingStep())
        context = pipeline.execute(context)
        
        # Build statistics
        statistics = {
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'columns': df.columns.tolist(),
            'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'missing_values': {col: int(v) for col, v in df.isnull().sum().items()},
            'sample_data': convert_to_serializable(df.head(5).to_dict('records')),
            'column_metadata': {name: convert_to_serializable({
                'inferred_type': meta.inferred_type,
                'confidence': meta.confidence,
                'missing_percentage': meta.missing_percentage,
                'unique_count': meta.unique_count,
                'is_identifier': meta.is_identifier,
                'statistics': meta.statistics
            }) for name, meta in context.metadata.items()}
        }
        
        # Update project
        project.original_filename = f"{db_type}://{database}/{source_name}"
        project.file_path = file_path
        project.row_count = len(df)
        project.column_count = len(df.columns)
        project.status = 'uploaded'
        project.statistics = statistics
        project.save()
        
        return Response({
            'message': f'Data imported successfully from {db_type.upper()}',
            'statistics': statistics
        })
    
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error importing from database: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
