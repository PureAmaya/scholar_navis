from .sqlite import SQLiteDatabase,db_type
from .sn_config import CONFIG
from datetime import datetime



def user_useage_log(request,user_name,llm_model,function_name,prompt,txt):
    if not CONFIG['enable_user_usage_log']:return
    user_useage_log_db = SQLiteDatabase(db_type.user_useage_log)
    ip = request.client['host']
    user_useage_log_db.insert_ingore('',['username','ip','datetime','llm_model', 'function_name','prompt','input']
                                    ,[user_name,ip,datetime.now().strftime("%Y-%m-%d %H-%M-%S"),llm_model,function_name,prompt,txt])