"""
Intelligent Alerting System for Proyecto Semilla
Proactive monitoring and notifications for system health
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    metric: str
    value: float
    threshold: float
    condition: str
    severity: str
    message: str
    timestamp: float
    status: str = "active"  # active, resolved, acknowledged


@dataclass
class AlertRule:
    """Alert rule configuration"""
    metric: str
    threshold: float
    condition: str  # 'above', 'below', 'equals'
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    enabled: bool = True
    cooldown_minutes: int = 5  # Minimum time between alerts


class AlertingEngine:
    """
    Intelligent alerting system with multiple notification channels
    """

    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.rules: Dict[str, AlertRule] = {}
        self.notification_channels: List[Dict[str, Any]] = []
        self.alert_history: List[Alert] = []
        self.max_history_size = 1000

        # Initialize default alert rules
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize default alerting rules"""
        default_rules = [
            # Performance rules
            AlertRule(
                metric="response_time_p95",
                threshold=500,
                condition="above",
                severity="high",
                description="Response time too high",
                cooldown_minutes=10
            ),
            AlertRule(
                metric="error_rate_percentage",
                threshold=5,
                condition="above",
                severity="critical",
                description="Error rate too high",
                cooldown_minutes=5
            ),
            AlertRule(
                metric="memory_usage_mb",
                threshold=500,
                condition="above",
                severity="medium",
                description="High memory usage",
                cooldown_minutes=15
            ),
            AlertRule(
                metric="cache_hit_rate",
                threshold=50,
                condition="below",
                severity="low",
                description="Low cache hit rate",
                cooldown_minutes=30
            ),
            # Security rules
            AlertRule(
                metric="failed_login_attempts_per_hour",
                threshold=10,
                condition="above",
                severity="high",
                description="High number of failed login attempts",
                cooldown_minutes=15
            ),
            AlertRule(
                metric="suspicious_requests_per_minute",
                threshold=20,
                condition="above",
                severity="critical",
                description="High number of suspicious requests detected",
                cooldown_minutes=5
            ),
            AlertRule(
                metric="blocked_ips_count",
                threshold=5,
                condition="above",
                severity="medium",
                description="Multiple IPs blocked by rate limiting",
                cooldown_minutes=10
            ),
            AlertRule(
                metric="sql_injection_attempts_per_hour",
                threshold=3,
                condition="above",
                severity="critical",
                description="SQL injection attempts detected",
                cooldown_minutes=5
            ),
            AlertRule(
                metric="xss_attempts_per_hour",
                threshold=3,
                condition="above",
                severity="high",
                description="XSS attempts detected",
                cooldown_minutes=10
            ),
            AlertRule(
                metric="unauthorized_access_attempts_per_hour",
                threshold=15,
                condition="above",
                severity="critical",
                description="High number of unauthorized access attempts",
                cooldown_minutes=5
            )
        ]

        for rule in default_rules:
            self.add_rule(rule)

    def add_rule(self, rule: AlertRule):
        """Add alert rule"""
        rule_id = f"{rule.metric}_{rule.condition}_{rule.threshold}"
        self.rules[rule_id] = rule

    def remove_rule(self, rule_id: str):
        """Remove alert rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]

    def add_notification_channel(self, channel_config: Dict[str, Any]):
        """Add notification channel"""
        self.notification_channels.append(channel_config)

    async def check_alerts(self, metrics: Dict[str, float]):
        """Check all alert rules against current metrics"""
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue

            if rule.metric in metrics:
                current_value = metrics[rule.metric]
                should_alert = self._evaluate_condition(current_value, rule)

                if should_alert:
                    await self._trigger_alert(rule, current_value, metrics)
                else:
                    # Check if we need to resolve existing alert
                    alert_key = f"{rule.metric}_{rule.condition}"
                    if alert_key in self.alerts:
                        await self._resolve_alert(alert_key)

    def _evaluate_condition(self, value: float, rule: AlertRule) -> bool:
        """Evaluate if alert condition is met"""
        if rule.condition == "above":
            return value > rule.threshold
        elif rule.condition == "below":
            return value < rule.threshold
        elif rule.condition == "equals":
            return abs(value - rule.threshold) < 0.01
        return False

    async def _trigger_alert(self, rule: AlertRule, value: float, all_metrics: Dict[str, float]):
        """Trigger alert for rule"""
        alert_key = f"{rule.metric}_{rule.condition}"

        # Check cooldown period
        if alert_key in self.alerts:
            last_alert = self.alerts[alert_key]
            cooldown_seconds = rule.cooldown_minutes * 60
            if time.time() - last_alert.timestamp < cooldown_seconds:
                return  # Still in cooldown

        # Create new alert
        alert = Alert(
            id=f"{alert_key}_{int(time.time())}",
            metric=rule.metric,
            value=value,
            threshold=rule.threshold,
            condition=rule.condition,
            severity=rule.severity,
            message=self._generate_alert_message(rule, value, all_metrics),
            timestamp=time.time(),
            status="active"
        )

        self.alerts[alert_key] = alert
        self.alert_history.append(alert)

        # Keep history size manageable
        if len(self.alert_history) > self.max_history_size:
            self.alert_history.pop(0)

        # Send notifications
        await self._send_notifications(alert)

        logging.warning(f"🚨 ALERT TRIGGERED: {alert.message}")

    async def _resolve_alert(self, alert_key: str):
        """Resolve existing alert"""
        if alert_key in self.alerts:
            alert = self.alerts[alert_key]
            if alert.status == "active":
                alert.status = "resolved"
                alert.timestamp = time.time()

                # Send resolution notification
                await self._send_resolution_notification(alert)

                logging.info(f"✅ ALERT RESOLVED: {alert.metric}")

    def _generate_alert_message(self, rule: AlertRule, value: float, all_metrics: Dict[str, float]) -> str:
        """Generate human-readable alert message"""
        if rule.metric == "response_time_p95":
            return f"Response time P95 is {value:.1f}ms (threshold: {rule.threshold}ms)"
        elif rule.metric == "error_rate_percentage":
            return f"Error rate is {value:.1f}% (threshold: {rule.threshold}%)"
        elif rule.metric == "memory_usage_mb":
            return f"Memory usage is {value:.1f}MB (threshold: {rule.threshold}MB)"
        elif rule.metric == "cache_hit_rate":
            return f"Cache hit rate is {value:.1f}% (threshold: {rule.threshold}%)"
        else:
            return f"{rule.metric} is {value} (threshold: {rule.threshold})"

    async def _send_notifications(self, alert: Alert):
        """Send alert notifications to all channels"""
        for channel in self.notification_channels:
            try:
                if channel.get("type") == "email":
                    await self._send_email_alert(alert, channel)
                elif channel.get("type") == "slack":
                    await self._send_slack_alert(alert, channel)
                elif channel.get("type") == "webhook":
                    await self._send_webhook_alert(alert, channel)
                elif channel.get("type") == "log":
                    logging.warning(f"ALERT: {alert.message}")
            except Exception as e:
                logging.error(f"Failed to send alert to {channel.get('type')}: {e}")

    async def _send_resolution_notification(self, alert: Alert):
        """Send alert resolution notifications"""
        resolution_message = f"✅ RESOLVED: {alert.metric} returned to normal"

        for channel in self.notification_channels:
            try:
                if channel.get("type") == "email":
                    await self._send_email_alert(alert, channel, resolution_message)
                elif channel.get("type") == "log":
                    logging.info(resolution_message)
            except Exception as e:
                logging.error(f"Failed to send resolution to {channel.get('type')}: {e}")

    async def _send_email_alert(self, alert: Alert, channel: Dict[str, Any], custom_message: str = None):
        """Send email alert"""
        if not all(key in channel for key in ["smtp_server", "smtp_port", "username", "password", "from", "to"]):
            logging.error("Email channel configuration incomplete")
            return

        message = custom_message or alert.message

        msg = MIMEMultipart()
        msg['From'] = channel["from"]
        msg['To'] = channel["to"]
        msg['Subject'] = f"🚨 Proyecto Semilla Alert - {alert.severity.upper()}"

        body = f"""
Proyecto Semilla System Alert

Severity: {alert.severity.upper()}
Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.timestamp))}

{message}

Please check the monitoring dashboard for more details.
https://proyecto-semilla.com/monitoring

---
Proyecto Semilla Monitoring System
        """.strip()

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(channel["smtp_server"], channel["smtp_port"])
            server.starttls()
            server.login(channel["username"], channel["password"])
            server.sendmail(channel["from"], channel["to"], msg.as_string())
            server.quit()
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")

    async def _send_slack_alert(self, alert: Alert, channel: Dict[str, Any]):
        """Send Slack alert (placeholder for future implementation)"""
        # TODO: Implement Slack webhook integration
        logging.info(f"Slack alert would be sent: {alert.message}")

    async def _send_webhook_alert(self, alert: Alert, channel: Dict[str, Any]):
        """Send webhook alert (placeholder for future implementation)"""
        # TODO: Implement generic webhook integration
        logging.info(f"Webhook alert would be sent: {alert.message}")

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return [
            {
                "id": alert.id,
                "metric": alert.metric,
                "value": alert.value,
                "threshold": alert.threshold,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.timestamp,
                "age_minutes": (time.time() - alert.timestamp) / 60
            }
            for alert in self.alerts.values()
            if alert.status == "active"
        ]

    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get alert history"""
        return [
            {
                "id": alert.id,
                "metric": alert.metric,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.timestamp,
                "status": alert.status
            }
            for alert in self.alert_history[-limit:]
        ]

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge alert"""
        for alert in self.alerts.values():
            if alert.id == alert_id:
                alert.status = "acknowledged"
                break


# Global alerting instance
alerting_engine = AlertingEngine()


def get_alerting_engine() -> AlertingEngine:
    """Dependency injection for alerting engine"""
    return alerting_engine