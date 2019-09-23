
from goods.shelfgoods.proxy import compare_col_equal,compare_col_max,compare_col_min,filter_wz_box
class ProxyFactory:
    checkbox_ins = None
    display_ins = None
    shelf_img = None
    factory_proxy = {
                'filter_wz_box':filter_wz_box,
                'compare_col_equal':compare_col_equal,
                'compare_col_min':compare_col_min,
                'compare_col_max':compare_col_max,
                     }
    def __init__(self,checkbox_ins,display_ins,shelf_img):
        self.checkbox_ins = checkbox_ins
        self.display_ins = display_ins
        self.shelf_img = shelf_img

    def process(self):
        proxy_names = self.get_proxy_process_name()
        checkbox_ins = None
        for proxy_name in proxy_names:
            checkbox_ins,display_ins = self.factory_proxy[proxy_name].process(self.checkbox_ins,self.display_ins,self.shelf_img)
        return checkbox_ins.gbx_ins
    def get_proxy_process_name(self):
        ck_col_nums = self.checkbox_ins.gbx_ins.level_columns
        ds_col_nums = self.display_ins.gbx_ins.level_columns
        if ck_col_nums == ds_col_nums:
            return ['filter_wz_box','compare_col_equal']
        elif ck_col_nums < ds_col_nums:
            return ['filter_wz_box', 'compare_col_min']
        elif ck_col_nums>ds_col_nums:
            return ['filter_wz_box', 'compare_col_min']




