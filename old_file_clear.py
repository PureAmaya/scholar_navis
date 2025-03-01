'''
Author: scholar_navis@PureAmaya
'''

import os
import shutil
from time import sleep
from datetime import datetime
from multiprocessing import Process,Lock
from shared_utils.config_loader import get_conf


# 需要自动清理的文件夹：
# tmp: tmp/default_user/2024-08-29 09-53-20/root_dir/sub_dir
# 总结库：\gpt_log\default_user\scholar_navis\lib （优先清理里面的lib_manifest.yml）
# 总结库之外的scholar_navis
# private_upload:private_upload\default_user\2024-08-29-09-48-56\files


# 运行之前，清除一下缓存
if os.path.exists('tmp'):shutil.rmtree('tmp')

AUTO_CLEAR_TMP,AUTO_CLEAR_GPT_LOG_DIR,AUTO_CLEAR_PRIVATE_UPLOAD = get_conf('AUTO_CLEAR_TMP','AUTO_CLEAR_GPT_LOG_DIR','AUTO_CLEAR_PRIVATE_UPLOAD')

thread_cycle_interval = 300
'''清理线程循环间隔（默认300）'''
tmp_lifespan = 600  
'''缓存文件最长寿命（默认600）（秒）'''
private_upload_lifespan = 3
'''private_upload文件夹最长寿命（小时）'''
gpt_log_lifespan = 5
'''gpt_log文件夹最长寿命（小时）'''

def _get_dir_to_delete(target_dir):
    assert target_dir == 'tmp' or target_dir =='gpt_log' or target_dir =='private_upload'
    
    could_del_dirs = []
    now = datetime.now()

    for root, dirs, files in os.walk(target_dir):

        if target_dir !='gpt_log' and len(root.split(os.sep))  != 3: continue
        if target_dir =='gpt_log' and len(root.split(os.sep))  != 4: continue # 只删除子文件夹！
        
        # 共享文件夹先不删除
        #if 'shared' == root.split(os.sep)[-1]:continue
        
        #print(root)
        try:
            dir_time =  datetime.fromtimestamp(os.path.getmtime(root))
            
            # 缓存应当由更加激进一些的删除策略
            if  target_dir == 'tmp':
                could_delete = (now - dir_time).seconds >= tmp_lifespan
            elif target_dir == 'private_upload':
                could_delete = (now - dir_time).seconds / 60 / 60 >= private_upload_lifespan
            else:
                could_delete = (now - dir_time).seconds / 60 / 60 >= gpt_log_lifespan
            
            if could_delete:could_del_dirs.append(root)
        except Exception as e:
            print(f"couldn't get directory time: {root}. {e}")
            
    if len(could_del_dirs) > 0 :print(f'these will be deleted: {could_del_dirs}')
    
    return could_del_dirs

        
def _delete_dir(target_dir,lock):
    # 删除缓存的在下面
    if AUTO_CLEAR_GPT_LOG_DIR and target_dir == 'gpt_log':
        to_del = _get_dir_to_delete(target_dir)
    elif AUTO_CLEAR_PRIVATE_UPLOAD and target_dir == 'private_upload':
        to_del = _get_dir_to_delete(target_dir)
    else:
        return
    
    for t in to_del:
        try:
            with lock:shutil.rmtree(t)
        except Exception as e:print(f"couldn't remove directory: {t}. {e}")
        
def _delete_tmp(lock):
    if not AUTO_CLEAR_TMP:return
    to_del = _get_dir_to_delete('tmp')
    for t in to_del:
        try:
            with lock:shutil.rmtree(t)
        except Exception as e:print(f"couldn't remove directory: {t}. {e}")
        

def _delete_old_files(lock):
    while True:
        try:
            _delete_tmp(lock)
            _delete_dir('private_upload',lock)
            _delete_dir('gpt_log',lock)
            sleep(thread_cycle_interval)
        except KeyboardInterrupt:
            exit(1)

    
def start_clear_old_files():
    os.makedirs('tmp',exist_ok=True)
    os.makedirs('gpt_log',exist_ok=True)
    os.makedirs('private_upload',exist_ok=True)
    
    if  AUTO_CLEAR_TMP or AUTO_CLEAR_PRIVATE_UPLOAD or AUTO_CLEAR_GPT_LOG_DIR:
        
        # 创建守护进程
        lock = Lock()
        daemon_process = Process(target=_delete_old_files,args=(lock,))
        daemon_process.daemon = True
        daemon_process.start()
        
        print('Automatic cleanup mode has been enabled.') 
        


if __name__ == "__main__":
    AUTO_CLEAR_TMP = True;AUTO_CLEAR_PRIVATE_UPLOAD= True;AUTO_CLEAR_GPT_LOG_DIR = True
    start_clear_old_files()
    while True:
        sleep(1)
