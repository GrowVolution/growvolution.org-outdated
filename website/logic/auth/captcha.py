from LIBRARY import *
from google.cloud.recaptchaenterprise_v1 import RecaptchaEnterpriseServiceClient, Event, Assessment, CreateAssessmentRequest
from website.rendering import render
from .verification import captcha_status, token_response

PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
CAPTCHA_ID_V3 = os.getenv('RECAPTCHA_ID_V3')
CAPTCHA_ID_V2 = os.getenv('RECAPTCHA_ID_V2')


def captcha_valid(token: str, fallback: bool) -> bool:
    client = RecaptchaEnterpriseServiceClient()

    event = Event()
    event.site_key = CAPTCHA_ID_V2 if fallback else CAPTCHA_ID_V3
    event.token = token
    event.user_ip_address = request.remote_addr
    event.user_agent = request.headers.get('User-Agent')
    event.ja3 = request.headers.get("X-JA3-Fingerprint")
    event.ja4 = request.headers.get("X-JA4-Fingerprint")

    assessment = Assessment()
    assessment.event = event

    project_name = f"projects/{PROJECT_ID}"

    assessment_request = CreateAssessmentRequest()
    assessment_request.assessment = assessment
    assessment_request.parent = project_name

    response = client.create_assessment(assessment_request)

    if not response.token_properties.valid:
        log('warn',
            f"Captcha check failed because of invalid token: "
            f"{str(response.token_properties.invalid_reason)}")
        return False

    action = 'verify'
    if response.token_properties.action != action:
        log('warn',
            f"Captcha check failed because of invalid action: {action}")
        return False
    else:
        log('info', f"Captcha risk analysis score: {str(response.risk_analysis.score)}")
        for reason in response.risk_analysis.reasons:
            log('info', f"Captcha risk analysis reason: {reason}")

    return True if response.risk_analysis.score > 0.5 else False


def _render_self(fallback: bool):
    return render('auth/captcha.html',
                  captcha_id=CAPTCHA_ID_V2 if fallback else CAPTCHA_ID_V3,
                  fallback=fallback)


def handle_request():
    fallback = False if captcha_status() == 'unverified' else True

    if request.method == 'POST':
        request_data = request.get_json()
        token = request_data.get('captcha_token')
        valid = captcha_valid(token, fallback)

        fingerprint = request_data.get('client_fingerprint')

        data = {
            'status': 'valid' if valid else 'invalid' if fallback else 'pending',
            'fingerprint': fingerprint
        }
        debug_response = f"Captcha {'v2' if fallback else 'v3'} {'passed' if valid else 'failed'}!"

        return token_response(data, 365, 'captcha_token', debug_response)

    return _render_self(fallback)
