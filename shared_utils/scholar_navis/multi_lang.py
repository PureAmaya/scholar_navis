'''
Author: scholar_navis@PureAmaya
'''

from i18n import text_i18n
from shared_utils.config_loader import get_conf

LANGUAGE_DISPLAY = get_conf('LANGUAGE_DISPLAY')



i18n = text_i18n(LANGUAGE_DISPLAY)
_ = i18n.gettext

selected_language = LANGUAGE_DISPLAY
'''目前选定的语言（显示）'''



    







