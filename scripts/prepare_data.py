import sagemaker
import boto3
from data.Diabetes import load_data
from sagemaker import get_execution_role

data = load_data()

# TODO: Schritt-für-Schritt-Anleitung:
"""
Rolle übernehmen:
Ersetze arn:aws:iam::123456789012:role/MyRoleName durch die ARN der Rolle, die du übernehmen möchtest, und MySessionName durch einen Namen für deine Sitzung.
bash

aws sts assume-role \
    --role-arn arn:aws:iam::123456789012:role/MyRoleName \
    --role-session-name MySessionName

Dieser Befehl gibt ein JSON-Dokument mit temporären Anmeldeinformationen zurück, das die AccessKeyId, SecretAccessKey und SessionToken enthält.
Temporäre Anmeldeinformationen verwenden:
Exportiere die temporären Anmeldeinformationen in deine Umgebungsvariablen. Ersetze YOUR_ACCESS_KEY_ID, YOUR_SECRET_ACCESS_KEY, und YOUR_SESSION_TOKEN durch die Werte, die du im vorherigen Schritt erhalten hast.
bash

export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
export AWS_SESSION_TOKEN=YOUR_SESSION_TOKEN

Verwenden der Rolle:
Nun kannst du die AWS CLI verwenden, und die Befehle werden mit den Berechtigungen der übernommenen Rolle ausgeführt.
bash

aws sagemaker list-training-jobs
"""

# Verwenden der Rolle über eine temporäre Sitzung
session = boto3.Session(
    aws_access_key_id='YOUR_ACCESS_KEY_ID',
    aws_secret_access_key='YOUR_SECRET_ACCESS_KEY',
    aws_session_token='YOUR_SESSION_TOKEN'
)

# Erstellen eines SageMaker-Clients
sagemaker_client = session.client('sagemaker')

# Beispiel: Liste der Training Jobs abrufen
response = sagemaker_client.list_training_jobs()
print(response)