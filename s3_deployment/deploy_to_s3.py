#!/usr/bin/env python3
"""
Deploy Business Unit Manager to S3 for DataApp Hub.

This script packages and uploads the app to S3 in the format expected by
the EDA Data Apps Hub's S3 app loader.

S3 Structure:
    s3://<bucket>/<env>/forms/data-management/business-unit-manager/
        ├── app.py
        ├── metadata.json
        └── requirements.txt
"""

import boto3
import json
import sys
import os
from pathlib import Path
from typing import Optional
import click
from botocore.exceptions import ClientError


def upload_file_to_s3(
    file_path: Path,
    bucket: str,
    s3_key: str,
    dry_run: bool = False
) -> bool:
    """Upload a file to S3."""
    if dry_run:
        print(f"[DRY RUN] Would upload: {file_path} -> s3://{bucket}/{s3_key}")
        return True

    try:
        s3_client = boto3.client('s3')
        s3_client.upload_file(
            str(file_path),
            bucket,
            s3_key,
            ExtraArgs={'ServerSideEncryption': 'AES256'}
        )
        print(f"[OK] Uploaded: {file_path.name} -> s3://{bucket}/{s3_key}")
        return True
    except ClientError as e:
        print(f"[ERROR] Failed to upload {file_path.name}: {e}")
        return False
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        return False


def verify_s3_files(bucket: str, prefix: str, dry_run: bool = False) -> bool:
    """Verify uploaded files exist in S3."""
    if dry_run:
        print(f"[DRY RUN] Would verify files at: s3://{bucket}/{prefix}")
        return True

    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if 'Contents' not in response:
            print(f"[ERROR] No files found at s3://{bucket}/{prefix}")
            return False

        files = [obj['Key'] for obj in response['Contents']]
        print(f"\n[OK] Found {len(files)} files in S3:")
        for file in files:
            print(f"  - {file}")

        # Check required files
        required = ['app.py', 'metadata.json', 'requirements.txt', 'secrets.toml']
        missing = []
        for req in required:
            if not any(req in f for f in files):
                missing.append(req)

        if missing:
            print(f"\n[ERROR] Missing required files: {', '.join(missing)}")
            return False

        print("\n[OK] All required files present")
        return True

    except ClientError as e:
        print(f"[ERROR] Failed to verify S3 files: {e}")
        return False


@click.command()
@click.option(
    '--bucket',
    default='com.raymourflanigan.data-apps-hub',
    help='S3 bucket name'
)
@click.option(
    '--env',
    default='staging',
    type=click.Choice(['staging', 'prod']),
    help='Environment (staging or prod)'
)
@click.option(
    '--app-type',
    default='forms',
    type=click.Choice(['forms', 'insights', 'agents']),
    help='App type (forms, insights, or agents)'
)
@click.option(
    '--category',
    default='data-management',
    help='App category'
)
@click.option(
    '--app-name',
    default='business-unit-manager',
    help='App identifier/folder name'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be uploaded without actually uploading'
)
@click.option(
    '--verify-only',
    is_flag=True,
    help='Only verify existing deployment without uploading'
)
def deploy(
    bucket: str,
    env: str,
    app_type: str,
    category: str,
    app_name: str,
    dry_run: bool,
    verify_only: bool
):
    """Deploy Business Unit Manager to S3 for DataApp Hub."""

    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # S3 prefix
    s3_prefix = f"{env}/{app_type}/{category}/{app_name}"

    print("="*70)
    print("BUSINESS UNIT MANAGER - S3 DEPLOYMENT")
    print("="*70)
    print(f"Bucket:      s3://{bucket}")
    print(f"Environment: {env}")
    print(f"App Type:    {app_type}")
    print(f"Category:    {category}")
    print(f"App Name:    {app_name}")
    print(f"S3 Path:     s3://{bucket}/{s3_prefix}/")
    if dry_run:
        print("\n[DRY RUN MODE - No actual uploads]")
    print("="*70)

    # Files to deploy
    files_to_deploy = [
        ('app.py', script_dir / 'app.py'),
        ('metadata.json', script_dir / 'metadata.json'),
        ('requirements.txt', script_dir / 'requirements.txt'),
        ('.streamlit/secrets.toml', script_dir / '.streamlit' / 'secrets.toml'),
    ]

    # Verify only mode
    if verify_only:
        print("\n[VERIFICATION MODE]")
        success = verify_s3_files(bucket, s3_prefix, dry_run)
        sys.exit(0 if success else 1)

    # Verify source files exist
    print("\n[1/3] Verifying source files...")
    all_exist = True
    for filename, filepath in files_to_deploy:
        if filepath.exists():
            print(f"[OK] Found: {filename}")
        else:
            print(f"[ERROR] Missing: {filename}")
            all_exist = False

    if not all_exist:
        print("\n[ERROR] Some source files are missing. Aborting.")
        sys.exit(1)

    # Validate metadata.json
    print("\n[2/3] Validating metadata.json...")
    try:
        with open(script_dir / 'metadata.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        required_fields = ['name', 'identifier', 'description', 'version', 'category', 'app_type']
        missing_fields = [field for field in required_fields if field not in metadata]

        if missing_fields:
            print(f"[ERROR] Missing required metadata fields: {', '.join(missing_fields)}")
            sys.exit(1)

        print(f"[OK] Metadata valid:")
        print(f"  - Name: {metadata['name']}")
        print(f"  - Version: {metadata['version']}")
        print(f"  - Type: {metadata['app_type']}")
        print(f"  - Category: {metadata['category']}")

    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in metadata.json: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"[ERROR] metadata.json not found")
        sys.exit(1)

    # Upload files to S3
    print(f"\n[3/3] Uploading to S3...")
    upload_success = True

    for filename, filepath in files_to_deploy:
        s3_key = f"{s3_prefix}/{filename}"
        if not upload_file_to_s3(filepath, bucket, s3_key, dry_run):
            upload_success = False

    # Verify deployment
    if upload_success and not dry_run:
        print("\n[VERIFICATION] Checking uploaded files...")
        verify_success = verify_s3_files(bucket, s3_prefix)

        if verify_success:
            print("\n" + "="*70)
            print("DEPLOYMENT SUCCESSFUL!")
            print("="*70)
            print(f"\nApp Location: s3://{bucket}/{s3_prefix}/")
            print(f"\nNext Steps:")
            print(f"  1. The DataApp Hub will auto-discover this app")
            print(f"  2. App will appear in: {app_type.title()} -> {category.replace('-', ' ').title()}")
            print(f"  3. Users with required groups can access it")
            print(f"\nRequired Groups (from metadata):")
            for group in metadata.get('required_groups', []):
                print(f"  - {group}")
            print(f"\nApp will be available at:")
            print(f"  https://your-hub-domain/{app_type}/{category}/{app_name}")
            print("="*70)
        else:
            print("\n[ERROR] Verification failed after upload")
            sys.exit(1)
    elif not upload_success:
        print("\n[ERROR] Some files failed to upload")
        sys.exit(1)


if __name__ == '__main__':
    deploy()
