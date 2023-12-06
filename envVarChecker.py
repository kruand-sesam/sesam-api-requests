import dotenv
import sesamutils


dotenv.load_dotenv()
logger = sesamutils.sesam_logger('env-var-checker', timestamp=True)

def checkEnvironmentVariables():
    required_env_vars = ["LOG_LEVEL", "SESAM_NODE_URL", "SESAM_NODE_JWT", "SESAM_SUBID"]
    variablesConfig = sesamutils.VariablesConfig(required_env_vars)
    if not variablesConfig.validate():
        return False
    else:
        return True