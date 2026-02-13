"""
Firebase Cloud Messaging (FCM) service for push notification delivery.
Supports dry-run mode when FCM_SERVER_KEY is not configured.
"""
import json
from typing import Dict, Any, List, Optional
import httpx

from app.config import settings


FCM_SEND_URL = "https://fcm.googleapis.com/fcm/send"


class FCMService:
    """Service class for sending push notifications via FCM."""

    @staticmethod
    def is_configured() -> bool:
        """Check if FCM is configured with a server key."""
        return bool(settings.FCM_SERVER_KEY)

    @staticmethod
    def send_to_device(
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a push notification to a single device.

        Args:
            device_token: FCM device token
            title: Notification title
            body: Notification body
            data: Optional data payload

        Returns:
            FCM response dict or dry-run result
        """
        if not FCMService.is_configured():
            print(f"[FCM DRY RUN] → {device_token[:20]}... | {title}: {body}")
            return {
                "dry_run": True,
                "success": 1,
                "failure": 0,
                "device_token": device_token[:20] + "..."
            }

        payload = {
            "to": device_token,
            "notification": {
                "title": title,
                "body": body,
                "sound": "default"
            }
        }

        if data:
            payload["data"] = data

        headers = {
            "Authorization": f"key={settings.FCM_SERVER_KEY}",
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    FCM_SEND_URL,
                    headers=headers,
                    json=payload
                )
                result = response.json()
                return result
        except Exception as e:
            print(f"[FCM ERROR] Failed to send to {device_token[:20]}...: {e}")
            return {
                "error": str(e),
                "success": 0,
                "failure": 1
            }

    @staticmethod
    def send_to_multiple_devices(
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a push notification to multiple devices.

        Args:
            device_tokens: List of FCM device tokens
            title: Notification title
            body: Notification body
            data: Optional data payload

        Returns:
            Aggregated FCM response dict
        """
        if not device_tokens:
            return {"success": 0, "failure": 0, "skipped": True}

        if not FCMService.is_configured():
            for token in device_tokens:
                print(f"[FCM DRY RUN] → {token[:20]}... | {title}: {body}")
            return {
                "dry_run": True,
                "success": len(device_tokens),
                "failure": 0,
                "device_count": len(device_tokens)
            }

        # FCM supports up to 1000 registration IDs per request
        payload = {
            "registration_ids": device_tokens,
            "notification": {
                "title": title,
                "body": body,
                "sound": "default"
            }
        }

        if data:
            payload["data"] = data

        headers = {
            "Authorization": f"key={settings.FCM_SERVER_KEY}",
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    FCM_SEND_URL,
                    headers=headers,
                    json=payload
                )
                result = response.json()
                return result
        except Exception as e:
            print(f"[FCM ERROR] Failed to send to {len(device_tokens)} devices: {e}")
            return {
                "error": str(e),
                "success": 0,
                "failure": len(device_tokens)
            }
