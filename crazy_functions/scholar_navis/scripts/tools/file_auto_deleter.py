import os
import shutil
import threading
from time import sleep
if __name__ == "__main__":from shared_utils.sn_config import CONFIG
else:from shared_utils.sn_config import CONFIG
from datetime import datetime

# 需要自动清理的文件夹：
# tmp: tmp/default_user/2024-08-29 09-53-20/root_dir/sub_dir
# 总结库：\gpt_log\default_user\scholar_navis\lib （优先清理里面的lib_manifest.yml）
# 总结库之外的gpt_log（先算了）
# private_upload:private_upload\default_user\2024-08-29-09-48-56\files

# 运行之前，清除一下缓存
if os.path.exists('tmp'):shutil.rmtree('tmp')

lock = threading.Lock()

auto_clear_tmp = CONFIG['auto_clear_tmp']
auto_clear_summary_lib = CONFIG['auto_clear_summary_lib']
auto_clear_private_upload = CONFIG['auto_clear_private_upload']

thread_cycle_interval = 300
'''清理线程循环间隔（默认300）'''
tmp_lifespan = 300
'''缓存文件最长寿命（默认300）（秒）'''
gpt_log_lifespan = 1
'''gpt_log文件夹最长寿命（天）'''
private_upload_lifespan = 1
'''private_upload文件夹最长寿命（天）'''

def _get_dir_to_delete(target_dir):
    assert target_dir == 'tmp' or target_dir =='gpt_log' or target_dir =='private_upload'
    
    could_del_dirs = []
    now = datetime.now()

    for root, dirs, files in os.walk(target_dir):

        if target_dir != 'gpt_log':
            if len(root.split(os.sep))  != 3: continue
            #print(root)
            try:
                dir_time =  datetime.strptime(os.path.basename(root),"%Y-%m-%d-%H-%M-%S")
                #print(dir_time.day)
                
                # 缓存应当由更加激进一些的删除策略
                could_delete = False
                if  target_dir == 'tmp':
                    could_delete = abs(now - dir_time).seconds >= tmp_lifespan
                else:
                    could_delete = abs(now - dir_time).days >= private_upload_lifespan
                if could_delete:could_del_dirs.append(root)
            except:continue
            
        else:
            if 'scholar_navis' not in root or len(root.split(os.sep))  != 4: continue
            if 'lib_manifest.yml' not in files:could_del_dirs.append(root);continue
            #print(root)
            #print(files)
            # 获取文件状态信息
            lib_manifest_fp = os.path.join(root,'lib_manifest.yml')
            file_creation_time = datetime.fromtimestamp(os.path.getctime(lib_manifest_fp))
            interval = (now - file_creation_time).days
            #print(interval)
            if interval >= gpt_log_lifespan:
                could_del_dirs.append(root)
            
    if len(could_del_dirs) > 0 :print(f'these will be deleted: {could_del_dirs}')
    return could_del_dirs

def _delete_log():
    to_del = _get_dir_to_delete('gpt_log')
    # 优先清除lib_manifest，防止意外读取到这个总结库
    for t in to_del:
        lib_manifest_fp = os.path.join(t,'lib_manifest.yml')
        if os.path.exists(lib_manifest_fp):
            try:
                with lock:os.remove(lib_manifest_fp)
            except Exception as e:print(f"couldn't remove file: {lib_manifest_fp}. {e}")
    
    # 之后清除目录
    for t in to_del:
        try:
            with lock:shutil.rmtree(t)
        except Exception as e:print(f"couldn't remove directory: {t}. {e}")
        
def _delete_pri():
    to_del = _get_dir_to_delete('private_upload')
    for t in to_del:
        try:
            with lock:shutil.rmtree(t)
        except Exception as e:print(f"couldn't remove directory: {t}. {e}")
        
def _delete_tmp():
    to_del = _get_dir_to_delete('tmp')
    for t in to_del:
        try:
            with lock:shutil.rmtree(t)
        except Exception as e:print(f"couldn't remove directory: {t}. {e}")
        

def _delete_old_files():
    cycle = 0
    while True:
        _delete_tmp();cycle += 1
        if cycle == 2:_delete_pri()
        if cycle == 4:_delete_log();cycle = 0
        sleep(thread_cycle_interval)
        # 缓存进行频次较高的删除操作，防止积累
        # 上传文件夹频率稍高，因为虽然有会出现比较多的文件，但是比起缓存来说还是少点
        # 总结库就不用那么高频率了
    
def start_clear_old_files():
    if auto_clear_tmp or auto_clear_summary_lib or auto_clear_private_upload:
        
        print('Automatic cleanup mode has been enabled.') 
        
        # 创建守护线程
        cleanup_thread = threading.Thread(target=_delete_old_files)
        cleanup_thread.daemon = True 

        # 启动守护线程
        cleanup_thread.start()
        
    else:
        del thread_cycle_interval 
        del tmp_lifespan
        del gpt_log_lifespan
        del private_upload_lifespan 


if __name__ == "__main__":
    start_clear_old_files()
    while True:
        sleep(1)
