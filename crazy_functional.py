'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2024-12-28
- To ensure compatibility, all original features have been removed, retaining only the functionalities added by scholar_naivs.
'''


def get_crazy_functions(lang):

    ###### SCHOLAR NAVIS START ########
    from shared_utils.scholar_navis.gpt_academic_handler import registrator
    function_plugins = registrator({},lang)
    ##### SCHOLAR NAVIS END - UNINSTALL: DELETE THESE #########


    return function_plugins
