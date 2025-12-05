import json
import os
from datetime import datetime

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None  # Si pymongo no está instalado, no rompe la app


class MongoManager:
    def __init__(self):
        """
        Inicializa la conexión a MongoDB usando app_config.json.
        Si falla, la app sigue funcionando sin BD.
        """
        self.client = None
        self.db = None
        self.collection = None

        try:
            # Cargar configuración
            config_path = os.path.join("config", "app_config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            mongo_uri = cfg.get("mongo_uri", None)
            db_name = cfg.get("database", "pmda")
            collection_name = cfg.get("collection", "logs")

            # Verificar si pymongo está instalado
            if MongoClient is None:
                print("pymongo no está instalado. No se registrarán eventos en BD.")
                return

            # Si no hay URI definida, omitir conexión
            if not mongo_uri:
                print("⚠ No se definió mongo_uri. BD desactivada.")
                return

            # Intentar conexión
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]

            # Test de conexión
            self.client.server_info()
            print(f"✔ Conectado a MongoDB: {db_name}/{collection_name}")

        except Exception as e:
            print(f"⚠ No fue posible conectar a MongoDB: {e}")
            self.client = None
            self.db = None
            self.collection = None

    def log_event(self, user, action):
        """
        Guarda un evento en la base de datos.
        Si la BD no está disponible, simplemente no hace nada.
        """
        if self.collection is None:
            # Evitar que el proyecto falle
            print(f"ℹ Evento (sin BD): {user} - {action}")
            return

        try:
            log_entry = {
                "user": user,
                "action": action,
                "timestamp": datetime.now().isoformat()
            }
            self.collection.insert_one(log_entry)
            print(f"✔ Evento guardado en BD: {log_entry}")

        except Exception as e:
            print(f"⚠ No se pudo registrar evento en BD: {e}")
