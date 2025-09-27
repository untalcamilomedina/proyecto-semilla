"""
Basic Report Service for Proyecto Semilla
Handles scheduled report generation and delivery
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import UUID
import logging
import json

from sqlalchemy.orm import Session

from app.models.analytics import AnalyticsReport
from app.services.analytics_service import AnalyticsService
from app.core.database import get_db

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating and managing scheduled reports"""

    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)

    def generate_daily_report(self, tenant_id: UUID, report_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a daily analytics report for a tenant
        """
        if report_date is None:
            report_date = datetime.utcnow() - timedelta(days=1)

        try:
            # Get analytics summary
            summary = self.analytics_service.get_realtime_metrics(tenant_id, hours=24)

            # Get metrics data
            metrics_data = self.analytics_service.get_metrics(
                tenant_id=tenant_id,
                metric_names=['active_users', 'articles_published', 'api_requests', 'errors', 'page_views'],
                time_bucket='day',
                days=7
            )

            # Generate report content
            report_content = {
                'report_type': 'daily',
                'tenant_id': str(tenant_id),
                'report_date': report_date.isoformat(),
                'generated_at': datetime.utcnow().isoformat(),
                'summary': summary,
                'metrics': metrics_data,
                'insights': self._generate_insights(metrics_data, summary)
            }

            logger.info(f"Generated daily report for tenant {tenant_id}")
            return report_content

        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            raise

    def generate_weekly_report(self, tenant_id: UUID, week_start: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a weekly analytics report for a tenant
        """
        if week_start is None:
            # Get the start of the previous week (Monday)
            today = datetime.utcnow()
            week_start = today - timedelta(days=today.weekday() + 7)

        week_end = week_start + timedelta(days=6)

        try:
            # Get metrics for the week
            metrics_data = self.analytics_service.get_metrics(
                tenant_id=tenant_id,
                metric_names=['active_users', 'articles_published', 'api_requests', 'errors', 'page_views'],
                time_bucket='day',
                days=7
            )

            # Calculate weekly totals
            weekly_totals = {}
            for metric_name, data_points in metrics_data.items():
                total = sum(point['value'] for point in data_points)
                average = total / len(data_points) if data_points else 0
                weekly_totals[metric_name] = {
                    'total': total,
                    'average': average,
                    'data_points': len(data_points)
                }

            # Generate report content
            report_content = {
                'report_type': 'weekly',
                'tenant_id': str(tenant_id),
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'generated_at': datetime.utcnow().isoformat(),
                'weekly_totals': weekly_totals,
                'daily_breakdown': metrics_data,
                'insights': self._generate_weekly_insights(metrics_data, weekly_totals)
            }

            logger.info(f"Generated weekly report for tenant {tenant_id}")
            return report_content

        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            raise

    def _generate_insights(self, metrics_data: Dict[str, List[Dict[str, Any]]],
                          summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate insights from metrics data
        """
        insights = []

        # Check for error spikes
        if summary.get('errors_last_24h', 0) > 10:
            insights.append({
                'type': 'warning',
                'title': 'Alto número de errores',
                'description': f'Se detectaron {summary["errors_last_24h"]} errores en las últimas 24 horas',
                'recommendation': 'Revisar logs de error y rendimiento del sistema'
            })

        # Check for low activity
        if summary.get('active_users_24h', 0) < 5:
            insights.append({
                'type': 'info',
                'title': 'Baja actividad de usuarios',
                'description': f'Solo {summary["active_users_24h"]} usuarios activos en las últimas 24 horas',
                'recommendation': 'Considerar estrategias para aumentar engagement'
            })

        # Check for high API usage
        if summary.get('events_last_24h', 0) > 1000:
            insights.append({
                'type': 'success',
                'title': 'Alta actividad',
                'description': f'{summary["events_last_24h"]} eventos registrados en las últimas 24 horas',
                'recommendation': 'El sistema está funcionando correctamente'
            })

        return insights

    def _generate_weekly_insights(self, metrics_data: Dict[str, List[Dict[str, Any]]],
                                 weekly_totals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate weekly insights
        """
        insights = []

        # Check weekly trends
        active_users_total = weekly_totals.get('active_users', {}).get('total', 0)
        if active_users_total > 50:
            insights.append({
                'type': 'success',
                'title': 'Buena participación semanal',
                'description': f'{active_users_total} usuarios activos durante la semana',
                'recommendation': 'Mantener las estrategias actuales de engagement'
            })

        articles_total = weekly_totals.get('articles_published', {}).get('total', 0)
        if articles_total > 10:
            insights.append({
                'type': 'success',
                'title': 'Alta productividad de contenido',
                'description': f'{articles_total} artículos publicados durante la semana',
                'recommendation': 'Continuar con la frecuencia de publicación actual'
            })

        return insights

    def send_report_email(self, report_content: Dict[str, Any], recipients: List[str]) -> bool:
        """
        Send report via email (placeholder for actual email implementation)
        """
        try:
            # This is a placeholder for email sending functionality
            # In a real implementation, you would integrate with an email service
            logger.info(f"Report would be sent to {len(recipients)} recipients")
            logger.info(f"Report summary: {report_content.get('summary', {})}")

            # For now, just log the report
            return True

        except Exception as e:
            logger.error(f"Error sending report email: {e}")
            return False

    def process_scheduled_reports(self) -> Dict[str, Any]:
        """
        Process all active scheduled reports
        """
        try:
            # Get all active reports that are due
            now = datetime.utcnow()
            due_reports = self.db.query(AnalyticsReport).filter(
                AnalyticsReport.is_active == 'active',
                AnalyticsReport.next_run_at <= now
            ).all()

            results = {
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'reports': []
            }

            for report in due_reports:
                try:
                    # Generate report based on type
                    if report.report_type == 'daily':
                        report_content = self.generate_daily_report(report.tenant_id)
                    elif report.report_type == 'weekly':
                        report_content = self.generate_weekly_report(report.tenant_id)
                    else:
                        continue

                    # Send to recipients if configured
                    if report.recipients:
                        recipients = json.loads(report.recipients)
                        success = self.send_report_email(report_content, recipients)
                        if success:
                            results['successful'] += 1
                        else:
                            results['failed'] += 1
                    else:
                        results['successful'] += 1

                    # Update report metadata
                    report.last_run_at = now

                    # Calculate next run time based on schedule
                    if report.report_type == 'daily':
                        report.next_run_at = now + timedelta(days=1)
                    elif report.report_type == 'weekly':
                        report.next_run_at = now + timedelta(days=7)

                    results['processed'] += 1
                    results['reports'].append({
                        'id': str(report.id),
                        'name': report.name,
                        'type': report.report_type,
                        'status': 'success'
                    })

                except Exception as e:
                    logger.error(f"Error processing report {report.id}: {e}")
                    results['failed'] += 1
                    results['reports'].append({
                        'id': str(report.id),
                        'name': report.name,
                        'type': report.report_type,
                        'status': 'failed',
                        'error': str(e)
                    })

            self.db.commit()
            logger.info(f"Processed {results['processed']} scheduled reports")

            return results

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing scheduled reports: {e}")
            raise


# Utility functions for background tasks
def process_all_scheduled_reports(db: Session) -> Dict[str, Any]:
    """
    Process all scheduled reports (background task)
    """
    service = ReportService(db)
    return service.process_scheduled_reports()


def generate_tenant_daily_reports(db: Session) -> Dict[str, Any]:
    """
    Generate daily reports for all tenants (background task)
    """
    from app.models.tenant import Tenant

    results = {}
    service = ReportService(db)

    try:
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()

        for tenant in tenants:
            try:
                report = service.generate_daily_report(tenant.id)
                results[str(tenant.id)] = report
            except Exception as e:
                logger.error(f"Error generating daily report for tenant {tenant.id}: {e}")
                results[str(tenant.id)] = {'error': str(e)}

        return results

    except Exception as e:
        logger.error(f"Error in daily report generation: {e}")
        raise