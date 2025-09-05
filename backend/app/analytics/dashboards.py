"""
Interactive Dashboards for Real-Time Analytics
Dynamic dashboard system with customizable widgets and real-time updates
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
import asyncio
import uuid

from .models import DashboardModel, DashboardWidget, MetricData
from .engine import RealTimeAnalyticsEngine

@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    id: str
    name: str
    description: str
    tenant_id: Optional[str]
    user_id: str
    widgets: List[DashboardWidget]
    layout: Dict[str, Any]
    is_public: bool = False
    auto_refresh: int = 30  # seconds
    theme: str = "default"

@dataclass
class WidgetData:
    """Widget data for real-time updates"""
    widget_id: str
    data: Any
    timestamp: datetime
    refresh_interval: int

class DashboardManager:
    """
    Manages interactive dashboards with real-time updates
    """

    def __init__(self, analytics_engine: RealTimeAnalyticsEngine):
        self.analytics_engine = analytics_engine
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.active_connections: Dict[str, List[Any]] = {}
        self.widget_cache: Dict[str, WidgetData] = {}

    async def create_dashboard(self, config: Dict[str, Any]) -> str:
        """Create a new dashboard"""
        dashboard_id = str(uuid.uuid4())

        dashboard = DashboardConfig(
            id=dashboard_id,
            name=config["name"],
            description=config.get("description", ""),
            tenant_id=config.get("tenant_id"),
            user_id=config["user_id"],
            widgets=[],
            layout=config.get("layout", {}),
            is_public=config.get("is_public", False),
            auto_refresh=config.get("auto_refresh", 30),
            theme=config.get("theme", "default")
        )

        # Add widgets
        for widget_config in config.get("widgets", []):
            widget = DashboardWidget(
                id=str(uuid.uuid4()),
                title=widget_config["title"],
                type=widget_config["type"],
                data_source=widget_config["data_source"],
                config=widget_config.get("config", {}),
                position=widget_config["position"],
                refresh_interval=widget_config.get("refresh_interval", 30)
            )
            dashboard.widgets.append(widget)

        self.dashboards[dashboard_id] = dashboard
        return dashboard_id

    async def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> bool:
        """Update dashboard configuration"""
        if dashboard_id not in self.dashboards:
            return False

        dashboard = self.dashboards[dashboard_id]

        # Update basic properties
        for key, value in updates.items():
            if hasattr(dashboard, key):
                setattr(dashboard, key, value)

        # Notify connected clients
        await self._notify_dashboard_update(dashboard_id, updates)

        return True

    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete dashboard"""
        if dashboard_id not in self.dashboards:
            return False

        del self.dashboards[dashboard_id]

        # Clean up connections
        if dashboard_id in self.active_connections:
            del self.active_connections[dashboard_id]

        return True

    async def get_dashboard_data(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Get dashboard with current data"""
        if dashboard_id not in self.dashboards:
            return None

        dashboard = self.dashboards[dashboard_id]

        # Get data for all widgets
        widgets_data = []
        for widget in dashboard.widgets:
            widget_data = await self._get_widget_data(widget)
            widgets_data.append({
                "id": widget.id,
                "title": widget.title,
                "type": widget.type,
                "data": widget_data,
                "position": widget.position,
                "config": widget.config
            })

        return {
            "id": dashboard.id,
            "name": dashboard.name,
            "description": dashboard.description,
            "widgets": widgets_data,
            "layout": dashboard.layout,
            "theme": dashboard.theme,
            "auto_refresh": dashboard.auto_refresh
        }

    async def subscribe_to_dashboard(self, dashboard_id: str, websocket) -> AsyncGenerator[Dict[str, Any], None]:
        """Subscribe to real-time dashboard updates"""
        if dashboard_id not in self.dashboards:
            return

        # Add connection
        if dashboard_id not in self.active_connections:
            self.active_connections[dashboard_id] = []
        self.active_connections[dashboard_id].append(websocket)

        try:
            # Send initial data
            initial_data = await self.get_dashboard_data(dashboard_id)
            if initial_data:
                yield {"type": "initial", "data": initial_data}

            # Send periodic updates
            while True:
                await asyncio.sleep(self.dashboards[dashboard_id].auto_refresh)

                # Check if connection is still active
                if websocket not in self.active_connections.get(dashboard_id, []):
                    break

                # Send updated data
                updated_data = await self.get_dashboard_data(dashboard_id)
                if updated_data:
                    yield {"type": "update", "data": updated_data}

        finally:
            # Remove connection
            if dashboard_id in self.active_connections:
                if websocket in self.active_connections[dashboard_id]:
                    self.active_connections[dashboard_id].remove(websocket)

    async def _get_widget_data(self, widget: DashboardWidget) -> Any:
        """Get data for a specific widget"""
        cache_key = f"{widget.id}_{widget.data_source}"

        # Check cache first
        if cache_key in self.widget_cache:
            cached = self.widget_cache[cache_key]
            if (datetime.utcnow() - cached.timestamp).seconds < widget.refresh_interval:
                return cached.data

        # Get data based on widget type
        if widget.type == "metric":
            data = await self._get_metric_widget_data(widget)
        elif widget.type == "chart":
            data = await self._get_chart_widget_data(widget)
        elif widget.type == "table":
            data = await self._get_table_widget_data(widget)
        elif widget.type == "map":
            data = await self._get_map_widget_data(widget)
        else:
            data = {"error": f"Unknown widget type: {widget.type}"}

        # Cache result
        self.widget_cache[cache_key] = WidgetData(
            widget_id=widget.id,
            data=data,
            timestamp=datetime.utcnow(),
            refresh_interval=widget.refresh_interval
        )

        return data

    async def _get_metric_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for metric widget"""
        metric_name = widget.config.get("metric_name", widget.data_source)
        time_window = widget.config.get("time_window", 3600)

        metrics = await self.analytics_engine.get_real_time_metrics(
            metric_name, time_window
        )

        return {
            "value": metrics.get("sum", 0),
            "change": self._calculate_change_percentage(metrics),
            "trend": self._determine_trend(metrics),
            "time_window": time_window
        }

    async def _get_chart_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for chart widget"""
        chart_type = widget.config.get("chart_type", "line")
        metric_name = widget.config.get("metric_name", widget.data_source)
        time_window = widget.config.get("time_window", 3600)
        interval = widget.config.get("interval", 300)  # 5 minutes

        # Get time series data
        data_points = []
        current_time = datetime.utcnow()

        for i in range(time_window // interval):
            point_time = current_time - timedelta(seconds=i * interval)
            # This would need to be implemented to get historical data
            # For now, return mock data
            data_points.append({
                "timestamp": point_time.isoformat(),
                "value": 100 + (i % 10) * 10
            })

        return {
            "chart_type": chart_type,
            "data": data_points[::-1],  # Reverse to chronological order
            "metric_name": metric_name
        }

    async def _get_table_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for table widget"""
        # Mock table data - would be replaced with real data source
        return {
            "columns": ["Name", "Value", "Change"],
            "rows": [
                ["Page Views", 1250, "+12%"],
                ["Users", 89, "+5%"],
                ["Revenue", 12500, "+8%"],
                ["Errors", 3, "-50%"]
            ]
        }

    async def _get_map_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for map widget"""
        # Mock geographic data
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-74.0, 4.6]},
                    "properties": {"name": "Bogotá", "value": 150}
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-75.6, 6.2]},
                    "properties": {"name": "Medellín", "value": 120}
                }
            ]
        }

    def _calculate_change_percentage(self, metrics: Dict[str, Any]) -> float:
        """Calculate percentage change"""
        # Mock calculation - would use historical data
        return 12.5

    def _determine_trend(self, metrics: Dict[str, Any]) -> str:
        """Determine trend direction"""
        # Mock trend analysis
        return "up"

    async def _notify_dashboard_update(self, dashboard_id: str, updates: Dict[str, Any]):
        """Notify connected clients of dashboard updates"""
        if dashboard_id not in self.active_connections:
            return

        message = {
            "type": "dashboard_update",
            "dashboard_id": dashboard_id,
            "updates": updates,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Send to all connected clients
        for websocket in self.active_connections[dashboard_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                # Remove broken connection
                self.active_connections[dashboard_id].remove(websocket)

class WidgetTemplates:
    """Predefined widget templates"""

    @staticmethod
    def metric_widget(title: str, metric_name: str, position: Dict[str, int]) -> Dict[str, Any]:
        """Create metric widget template"""
        return {
            "title": title,
            "type": "metric",
            "data_source": metric_name,
            "config": {
                "metric_name": metric_name,
                "time_window": 3600,
                "show_trend": True,
                "show_change": True
            },
            "position": position,
            "refresh_interval": 30
        }

    @staticmethod
    def chart_widget(title: str, metric_name: str, chart_type: str,
                    position: Dict[str, int]) -> Dict[str, Any]:
        """Create chart widget template"""
        return {
            "title": title,
            "type": "chart",
            "data_source": metric_name,
            "config": {
                "chart_type": chart_type,
                "metric_name": metric_name,
                "time_window": 3600,
                "interval": 300,
                "show_legend": True,
                "colors": ["#3b82f6", "#10b981", "#f59e0b"]
            },
            "position": position,
            "refresh_interval": 60
        }

    @staticmethod
    def table_widget(title: str, data_source: str, position: Dict[str, int]) -> Dict[str, Any]:
        """Create table widget template"""
        return {
            "title": title,
            "type": "table",
            "data_source": data_source,
            "config": {
                "sortable": True,
                "filterable": True,
                "page_size": 10
            },
            "position": position,
            "refresh_interval": 300
        }

class DashboardPresets:
    """Predefined dashboard configurations"""

    @staticmethod
    def business_overview() -> Dict[str, Any]:
        """Business overview dashboard"""
        return {
            "name": "Business Overview",
            "description": "Key business metrics and KPIs",
            "widgets": [
                WidgetTemplates.metric_widget("Total Users", "user_count", {"x": 0, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.metric_widget("Revenue", "revenue_total", {"x": 3, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.metric_widget("Conversion Rate", "conversion_rate", {"x": 6, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.chart_widget("User Growth", "user_count", "line", {"x": 0, "y": 2, "width": 6, "height": 4}),
                WidgetTemplates.chart_widget("Revenue Trend", "revenue_total", "bar", {"x": 6, "y": 2, "width": 6, "height": 4}),
                WidgetTemplates.table_widget("Top Products", "products", {"x": 0, "y": 6, "width": 12, "height": 4})
            ],
            "layout": {"columns": 12, "rows": 10},
            "theme": "business"
        }

    @staticmethod
    def technical_monitoring() -> Dict[str, Any]:
        """Technical monitoring dashboard"""
        return {
            "name": "Technical Monitoring",
            "description": "System performance and health metrics",
            "widgets": [
                WidgetTemplates.metric_widget("Response Time", "response_time_avg", {"x": 0, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.metric_widget("Error Rate", "error_rate", {"x": 3, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.metric_widget("CPU Usage", "cpu_usage", {"x": 6, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.metric_widget("Memory Usage", "memory_usage", {"x": 9, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.chart_widget("Response Time Trend", "response_time_avg", "line", {"x": 0, "y": 2, "width": 6, "height": 4}),
                WidgetTemplates.chart_widget("Error Rate Trend", "error_rate", "area", {"x": 6, "y": 2, "width": 6, "height": 4}),
                WidgetTemplates.table_widget("Recent Errors", "error_logs", {"x": 0, "y": 6, "width": 12, "height": 4})
            ],
            "layout": {"columns": 12, "rows": 10},
            "theme": "technical"
        }

    @staticmethod
    def user_analytics() -> Dict[str, Any]:
        """User analytics dashboard"""
        return {
            "name": "User Analytics",
            "description": "User behavior and engagement metrics",
            "widgets": [
                WidgetTemplates.metric_widget("Active Users", "active_users", {"x": 0, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.metric_widget("Session Duration", "session_duration_avg", {"x": 3, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.metric_widget("Bounce Rate", "bounce_rate", {"x": 6, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.metric_widget("Retention Rate", "retention_rate", {"x": 9, "y": 0, "width": 3, "height": 2}),
                WidgetTemplates.chart_widget("User Flow", "user_flow", "sankey", {"x": 0, "y": 2, "width": 8, "height": 4}),
                WidgetTemplates.chart_widget("Device Types", "device_types", "pie", {"x": 8, "y": 2, "width": 4, "height": 4}),
                WidgetTemplates.table_widget("User Segments", "user_segments", {"x": 0, "y": 6, "width": 12, "height": 4})
            ],
            "layout": {"columns": 12, "rows": 10},
            "theme": "user"
        }

# Global dashboard manager instance
dashboard_manager = DashboardManager(None)  # Will be initialized with analytics engine

async def get_dashboard_manager() -> DashboardManager:
    """Dependency injection for dashboard manager"""
    return dashboard_manager

async def initialize_dashboard_manager(analytics_engine: RealTimeAnalyticsEngine):
    """Initialize dashboard manager with analytics engine"""
    global dashboard_manager
    dashboard_manager = DashboardManager(analytics_engine)