from fastapi import APIRouter
from app.api.v1.endpoints import (
    users, vehicles, maintenance, documents, 
    fuel_logs, freight_orders, clients, 
    costs, parts, tires, implements,
    reports, dashboard, admin, performance,
    journeys, fines, notifications, settings,
    vehicle_costs, vehicle_components,
    report_generator, telemetry, gps, leaderboard
)
# O endpoint 'login' foi removido

api_router = APIRouter()

# CORRIGIDO: Removida a rota de login (FASE 3)
# api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(fuel_logs.router, prefix="/fuel_logs", tags=["fuel_logs"])
api_router.include_router(freight_orders.router, prefix="/freight_orders", tags=["freight_orders"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(costs.router, prefix="/costs", tags=["costs"])
api_router.include_router(parts.router, prefix="/parts", tags=["parts"])
api_router.include_router(tires.router, prefix="/tires", tags=["tires"])
api_router.include_router(implements.router, prefix="/implements", tags=["implements"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(performance.router, prefix="/performance", tags=["performance"])
api_router.include_router(journeys.router, prefix="/journeys", tags=["journeys"])
api_router.include_router(fines.router, prefix="/fines", tags=["fines"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(vehicle_costs.router, prefix="/vehicle_costs", tags=["vehicle_costs"])
api_router.include_router(vehicle_components.router, prefix="/vehicle_components", tags=["vehicle_components"])
api_router.include_router(report_generator.router, prefix="/report-generator", tags=["report-generator"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
api_router.include_router(gps.router, prefix="/gps", tags=["gps"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])