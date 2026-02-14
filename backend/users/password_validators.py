"""
Password Validators - Government-grade password policy
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class GovernmentGradePasswordValidator:
    """
    Validates passwords according to government-grade security standards:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - No common patterns or sequences
    """
    
    def __init__(self, min_length=12):
        self.min_length = min_length
    
    def validate(self, password, user=None):
        errors = []
        
        # Length check
        if len(password) < self.min_length:
            errors.append(
                ValidationError(
                    _("Password must be at least %(min_length)d characters long."),
                    code='password_too_short',
                    params={'min_length': self.min_length}
                )
            )
        
        # Uppercase check
        if not re.search(r'[A-Z]', password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one uppercase letter."),
                    code='password_no_upper'
                )
            )
        
        # Lowercase check
        if not re.search(r'[a-z]', password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one lowercase letter."),
                    code='password_no_lower'
                )
            )
        
        # Digit check
        if not re.search(r'\d', password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one digit."),
                    code='password_no_digit'
                )
            )
        
        # Special character check
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
            errors.append(
                ValidationError(
                    _("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)."),
                    code='password_no_special'
                )
            )
        
        # Common sequences check
        common_sequences = [
            '123456', 'abcdef', 'qwerty', 'password', 'admin',
            '111111', '000000', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'abc123', 'pass123', '12345678'
        ]
        password_lower = password.lower()
        for seq in common_sequences:
            if seq in password_lower:
                errors.append(
                    ValidationError(
                        _("Password contains a common pattern that is not allowed."),
                        code='password_common_pattern'
                    )
                )
                break
        
        # Username in password check
        if user and user.email:
            email_parts = user.email.split('@')[0].lower()
            if len(email_parts) > 3 and email_parts in password_lower:
                errors.append(
                    ValidationError(
                        _("Password cannot contain your email address."),
                        code='password_contains_email'
                    )
                )
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _(
            "Your password must meet the following requirements:\n"
            "• At least 12 characters long\n"
            "• At least one uppercase letter (A-Z)\n"
            "• At least one lowercase letter (a-z)\n"
            "• At least one digit (0-9)\n"
            "• At least one special character (!@#$%^&*())\n"
            "• Cannot contain common patterns or your email"
        )


def validate_password_strength(password, user=None):
    """
    Validate password and return dict with results
    """
    result = {
        'valid': True,
        'errors': [],
        'strength': 0,
        'requirements': {
            'length': {'met': False, 'message': 'At least 12 characters'},
            'uppercase': {'met': False, 'message': 'One uppercase letter'},
            'lowercase': {'met': False, 'message': 'One lowercase letter'},
            'digit': {'met': False, 'message': 'One digit'},
            'special': {'met': False, 'message': 'One special character'},
        }
    }
    
    # Check each requirement
    if len(password) >= 12:
        result['requirements']['length']['met'] = True
        result['strength'] += 20
    else:
        result['errors'].append('Password must be at least 12 characters')
    
    if re.search(r'[A-Z]', password):
        result['requirements']['uppercase']['met'] = True
        result['strength'] += 20
    else:
        result['errors'].append('Password must contain an uppercase letter')
    
    if re.search(r'[a-z]', password):
        result['requirements']['lowercase']['met'] = True
        result['strength'] += 20
    else:
        result['errors'].append('Password must contain a lowercase letter')
    
    if re.search(r'\d', password):
        result['requirements']['digit']['met'] = True
        result['strength'] += 20
    else:
        result['errors'].append('Password must contain a digit')
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
        result['requirements']['special']['met'] = True
        result['strength'] += 20
    else:
        result['errors'].append('Password must contain a special character')
    
    result['valid'] = len(result['errors']) == 0
    
    return result
