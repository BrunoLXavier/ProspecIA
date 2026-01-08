"""
ProspecIA Backend - Main Application Entry Point

This module implements the FastAPI application following Clean Architecture principles.
Responsibilities:
- Application initialization
- Dependency injection setup
- Middleware configuration
- Router registration
- Lifecycle management (database, Kafka, Neo4j, AI models)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import structlog

from app.infrastructure.config.settings import get_settings
from app.infrastructure.middleware.logging_middleware import LoggingMiddleware
from app.infrastructure.middleware.auth_middleware import AuthMiddleware
from app.interfaces.http.routers import health, system, ingestao, consentimento

# Import adapters for initialization
from app.adapters.postgres import connection as postgres_conn
from app.adapters.neo4j import connection as neo4j_conn
from app.adapters.kafka import producer as kafka_prod
from app.adapters.minio import client as minio_cli

# Configure structured logging
logger = structlog.get_logger()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    
    Handles startup and shutdown events following Single Responsibility Principle.
    Initializes all external connections and resources.
    """
    # Startup
    logger.info(
        "application_startup",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENV,
    )
    
    try:
        # Initialize PostgreSQL connection
        logger.info("initializing_postgres")
        postgres_conn.db_connection = postgres_conn.DatabaseConnection(settings)
        await postgres_conn.db_connection.connect()
        logger.info("postgres_initialized")
        
        # Initialize Neo4j connection
        logger.info("initializing_neo4j")
        neo4j_conn.neo4j_connection = neo4j_conn.Neo4jConnection(settings)
        await neo4j_conn.neo4j_connection.connect()
        logger.info("neo4j_initialized")
        
        # Initialize Kafka producer
        logger.info("initializing_kafka")
        kafka_prod.kafka_producer = kafka_prod.KafkaProducerAdapter(settings)
        kafka_prod.kafka_producer.connect()
        logger.info("kafka_initialized")

        # Initialize MinIO client
        logger.info("initializing_minio")
        minio_cli.minio_client = minio_cli.MinioClientAdapter(settings)
        minio_cli.minio_client.connect()
        logger.info("minio_initialized")
        
        # TODO: Load BERTimbau model for LGPD agent
        # This will be done in use_cases/lgpd_agent.py
        
        logger.info("application_startup_complete")
        
    except Exception as e:
        logger.error(
            "application_startup_failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise
    
    yield
    
    # Shutdown
    logger.info("application_shutdown", app_name=settings.APP_NAME)
    
    try:
        # Close Kafka connection
        if kafka_prod.kafka_producer:
            kafka_prod.kafka_producer.disconnect()
            logger.info("kafka_disconnected")
        
        # Close Neo4j connection
        if neo4j_conn.neo4j_connection:
            await neo4j_conn.neo4j_connection.disconnect()
            logger.info("neo4j_disconnected")
        
        # Close PostgreSQL connection
        if postgres_conn.db_connection:
            await postgres_conn.db_connection.disconnect()
            logger.info("postgres_disconnected")
        
        logger.info("application_shutdown_complete")
        
    except Exception as e:
        logger.error(
            "application_shutdown_error",
            error=str(e),
            error_type=type(e).__name__,
        )


def create_application() -> FastAPI:
    """
    Application factory following Dependency Inversion Principle.
    
    Creates and configures the FastAPI application with all necessary
    middleware, routers, and settings.
    
    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Intelligent Research Prospecting and Management System with Responsible AI",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Configure CORS (Cross-Origin Resource Sharing)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Add authentication middleware (with settings)
    app.add_middleware(AuthMiddleware, settings=settings)
    
    # Register routers (Interface Segregation Principle)
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(system.router, prefix="/system", tags=["System"])
    app.include_router(ingestao.router)  # Already has prefix="/ingestions"
    app.include_router(consentimento.router)  # Already has prefix="/consents"
    
    # TODO: Register additional domain routers
    # app.include_router(fomento.router, prefix="/fontes-fomento", tags=["Fomento"])
    # app.include_router(clientes.router, prefix="/clientes", tags=["CRM"])
    # app.include_router(oportunidades.router, prefix="/oportunidades", tags=["Pipeline"])
    
    logger.info(
        "application_created",
        debug=settings.DEBUG,
        cors_origins=settings.CORS_ORIGINS,
        jwt_required=settings.FEATURE_JWT_REQUIRED,
    )
    
    return app


# Create application instance
app = create_application()


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.
    
    Returns:
        dict: API metadata
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "environment": settings.ENV,
    }
