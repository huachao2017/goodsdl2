import unittest
from goods.shelfdisplay.replacedisplay.display_object import Shelf, Level, DisplayGoods
from goods.shelfdisplay.replacedisplay.area_manager import AreaManager
from goods.shelfdisplay.replacedisplay.test.temporary_object import TestGoods, get_level_to_display_goods_name


class Test1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_bottom_level(self):
        shelf = Shelf(1, 510, 340, 300)
        shelf.levels.append(Level(shelf, 0, 170, 300))
        shelf.levels.append(Level(shelf, 1, 170, 300))
        shelf.levels.append(Level(shelf, 2, 170, 300))
        levelid_to_displaygoods_list = {
            0: [DisplayGoods(TestGoods('c2_1', 'c3_1', '1', 120, 58, 10, 0, 0),face_num=2),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '1', 120, 58, 10, 0, 0),face_num=2),
                DisplayGoods(TestGoods('c2_1', 'c3_2', '2', 120, 52, 10, 0, 0))],
            1: [DisplayGoods(TestGoods('c2_3', 'c3_4', '14', 120, 68, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_3', 'c3_4', '13', 120, 68, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_3', 'c3_4', '12', 120, 68, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_3', '11', 120, 62, 10, 0, 0))],
            2: [DisplayGoods(TestGoods('c2_3', 'c3_5', '21', 120, 70, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_3', 'c3_5', '22', 120, 70, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_4', 'c3_6', '23', 120, 68, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_4', 'c3_6', '24', 120, 68, 10, 0, 0))],
        }
        shelf.levels[0].display_goods_list = levelid_to_displaygoods_list[0]
        shelf.levels[1].display_goods_list = levelid_to_displaygoods_list[1]
        shelf.levels[2].display_goods_list = levelid_to_displaygoods_list[2]

        choose_goods_list = [
            TestGoods('c2_1', 'c3_1', '101', 100, 50, 20, 1, 0),  # 上架
            TestGoods('c2_3', 'c3_4', '102', 100, 68, 20, 1, 0),  # 上架
        ]

        area_manager = AreaManager(shelf, levelid_to_displaygoods_list, choose_goods_list)

        area_manager._first_born_areas()
        area_manager._second_combine_areas()
        area_manager._prepare_area_base_data()

        area_manager._prepare_area_calculate_data()
        area_manager._arrange_areas()
        area_manager._print_choose_goods_info()

        best_candidate_shelf = area_manager.arrange_goods()
        level_to_display_goods_name_str = get_level_to_display_goods_name(best_candidate_shelf)

        self.assertIn(level_to_display_goods_name_str[0], ['101,1,1,1,1,2,null,', '1,1,1,1,101,2,null,'])
        self.assertEqual(level_to_display_goods_name_str[1], '11,102,12,13,14,')
        self.assertEqual(level_to_display_goods_name_str[2], '21,22,23,24,null,')
        print(shelf)
        print(best_candidate_shelf)


