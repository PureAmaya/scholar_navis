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
dirs_lifespan = 1
'''private_upload和gpt_log文件夹最长寿命（天）'''

def _get_dir_to_delete(target_dir):
    assert target_dir == 'tmp' or target_dir =='gpt_log' or target_dir =='private_upload'
    
    could_del_dirs = []
    now = datetime.now()

    for root, dirs, files in os.walk(target_dir):

        if target_dir !='gpt_log' and len(root.split(os.sep))  != 3: continue
        if target_dir =='gpt_log' and len(root.split(os.sep))  != 4: continue
        
        # 共享文件夹先不删除
        if 'shared' == root.split(os.sep)[-1]:continue
        
        #print(root)
        #try:
        dir_time =  datetime.fromtimestamp(os.path.getmtime(root))
        
        # 缓存应当由更加激进一些的删除策略
        if  target_dir == 'tmp':
            could_delete = (now - dir_time).seconds >= tmp_lifespan
        else:
            #print(f'{now}  {dir_time}  {abs(now - dir_time).min}')
            could_delete = (now - dir_time).days >= dirs_lifespan
        
        if could_delete:could_del_dirs.append(root)
        #except:continue
            
    if len(could_del_dirs) > 0 :print(f'these will be deleted: {could_del_dirs}')
    
    return could_del_dirs

        
def _delete_dir(target_dir,lock):
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
    cycle = 0
    while True:
        _delete_tmp(lock);cycle += 1
        if cycle == 2:_delete_dir('private_upload',lock)
        if cycle == 4:_delete_dir('gpt_log',lock);cycle = 0
        sleep(thread_cycle_interval)
        # 缓存进行频次较高的删除操作，防止积累
        # 上传文件夹频率稍高，因为虽然有会出现比较多的文件，但是比起缓存来说还是少点
        # 总结库就不用那么高频率了
    
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
