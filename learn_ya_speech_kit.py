import os
import time
import json
import grpc
import requests

from tqdm import tqdm
from pathlib import Path
from yandex.cloud.ai.stt.v2 import stt_service_pb2, stt_service_pb2_grpc

def load_config():
    """Load configuration from config.json file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            
        required_fields = ['folder_id', 'language_code', 'oauth_token']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            print(f"Error: Missing required fields in config.json: {', '.join(missing_fields)}")
            print("Please make sure config.json contains all required fields:")
            print("""
{
    "folder_id": "your-folder-id",
    "language_code": "ru-RU",
    "oauth_token": "your-oauth-token"
}
            """)
            raise ValueError("Invalid config format")
            
        return config
    except FileNotFoundError:
        print("Error: config.json file not found!")
        print("Please create config.json with the following content:")
        print("""
{
    "folder_id": "your-folder-id",
    "language_code": "ru-RU",
    "oauth_token": "your-oauth-token"
}
        """)
        raise

def get_iam_token(oauth_token):
    """Get IAM token using OAuth token."""
    try:
        response = requests.post(
            'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            json={'yandexPassportOauthToken': oauth_token}
        )
        response.raise_for_status()
        return response.json().get('iamToken')
    except requests.exceptions.RequestException as e:
        print("Error getting IAM token!")
        print("Please make sure your OAuth token is valid.")
        print("You can get an OAuth token here: https://oauth.yandex.ru/authorize?response_type=token&client_id=1a6990aa636648e9b2ef855fa7bec2fb")
        raise

def read_audio_file(audio_file_path):
    """
    Read audio file and return its content as bytes.
    
    Args:
        audio_file_path (str): Path to the audio file
    
    Returns:
        bytes: Audio content
    """
    try:
        with open(audio_file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Audio file '{audio_file_path}' not found!")
        raise

def transcribe_audio(audio_content, config):
    """
    Transcribe audio using Yandex Speech Kit.
    
    Args:
        audio_content (bytes): Audio file content
        config (dict): Configuration containing folder_id and other settings
    
    Returns:
        str: Transcribed text
    """
    # Create SSL credentials
    cred = grpc.ssl_channel_credentials()
    
    # Create channel and stub
    channel = grpc.secure_channel('stt.api.cloud.yandex.net:443', cred)
    stub = stt_service_pb2_grpc.SttServiceStub(channel)

    # Create specification
    spec = stt_service_pb2.RecognitionSpec(
        language_code=config['language_code'],
        profanity_filter=False,
        model='general',
        partial_results=False,
        audio_encoding='OGG_OPUS',
        sample_rate_hertz=48000
    )

    # Create config
    recognition_config = stt_service_pb2.RecognitionConfig(
        specification=spec,
        folder_id=config['folder_id']
    )

    # Create audio
    audio = stt_service_pb2.RecognitionAudio(content=audio_content)

    # Get IAM token using OAuth token
    iam_token = get_iam_token(config['oauth_token'])
    metadata = (('authorization', f'Bearer {iam_token}'),)

    try:
        # Send the request and get response
        request = stt_service_pb2.LongRunningRecognitionRequest(config=recognition_config, audio=audio)
        operation = stub.LongRunningRecognize(request, metadata=metadata)
        
        print("Waiting for operation to complete...")
        
        # Wait for the operation to complete
        while True:
            result = stub.GetLongRunningRecognitionTask(
                stt_service_pb2.GetLongRunningRecognitionTaskRequest(id=operation.id),
                metadata=metadata
            )
            if result.done:
                break
            time.sleep(1)
            print(".", end="", flush=True)
        
        print("\nProcessing results...")
        
        # Process the results
        chunks = []
        for chunk in result.response.chunks:
            chunks.append(chunk.alternatives[0].text)
        
        return ' '.join(chunks)
    
    except grpc.RpcError as e:
        print(f"gRPC error details: {e.details()}")
        raise

def main():
    # Load configuration
    config = load_config()
    AUDIO_FILE = '15s.m4a'  # Your M4A file path

    try:
        print("Reading audio file...")
        audio_content = read_audio_file(AUDIO_FILE)
        
        print("Starting transcription...")
        transcribed_text = transcribe_audio(audio_content, config)
        print("\nTranscription result:")
        print(transcribed_text)
        
        # Save result to file
        with open('transcription_result.txt', 'w', encoding='utf-8') as f:
            f.write(transcribed_text)
            
        print("\nTranscription has been saved to 'transcription_result.txt'")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
