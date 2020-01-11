import unittest
from goods.shelfdisplay.replacedisplay.display_object import Shelf, Level, DisplayGoods
from goods.shelfdisplay.replacedisplay.area_manager import AreaManager
from goods.shelfdisplay.replacedisplay.test.temporary_object import TestGoods


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
        shelf = Shelf(1, 1800, 600, 300)
        shelf.levels.append(Level(shelf, 0, 360, 300))
        shelf.levels.append(Level(shelf, 1, 360, 300))
        shelf.levels.append(Level(shelf, 2, 360, 300))
        shelf.levels.append(Level(shelf, 3, 360, 300))
        shelf.levels.append(Level(shelf, 4, 360, 300))
        levelid_to_displaygoods_list = {
            1: [DisplayGoods(TestGoods('c2_1', 'c3_3', '18', 150, 40, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '17', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '16', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '15', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '14', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '13', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '12', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '11', 150, 80, 10, 0, 0))],
            2: [DisplayGoods(TestGoods('c2_1', 'c3_3', '21', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '22', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '23', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '24', 100, 80, 9, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '25', 100, 80, 8, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '26', 100, 80, 7, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '27', 100, 80, 6, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '28', 100, 40, 5, 0, 0))],
        }
        shelf.levels[1].display_goods_list = levelid_to_displaygoods_list[1]
        shelf.levels[2].display_goods_list = levelid_to_displaygoods_list[2]

        choose_goods_list = []

        area_manager = AreaManager(shelf, levelid_to_displaygoods_list, choose_goods_list)

        area_manager._first_born_areas()
        for area in area_manager.area_list:
            print(area)
        area_manager._second_combine_areas()
        for area in area_manager.area_list:
            print(area)
        area_manager._prepare_area_base_data()

        area_manager._prepare_area_calculate_data()
        area_manager._print_choose_goods_info()
        area_manager._arrange_areas()

        candidate_shelf_list = area_manager._generate_all_area_candidate()

        self.assertEqual(len(candidate_shelf_list), 1)
        # for shelf_list in candidate_shelf_list:
        #     print(shelf_list)

        best_candidate_shelf = area_manager.calculate_best_candidate_shelf(candidate_shelf_list)
        level_to_display_goods_name_str = get_level_to_display_goods_name(best_candidate_shelf)

        self.assertEqual(level_to_display_goods_name_str[0], 'null,')
        self.assertEqual(level_to_display_goods_name_str[1], '11,12,13,14,15,16,17,18,')
        self.assertEqual(level_to_display_goods_name_str[2], '21,22,23,24,25,26,27,28,')
        print(shelf)
        print(best_candidate_shelf)

    def test_no_two_bottom_level(self):
        shelf = Shelf(1, 1800, 600, 300)
        shelf.levels.append(Level(shelf, 0, 360, 300))
        shelf.levels.append(Level(shelf, 1, 360, 300))
        shelf.levels.append(Level(shelf, 2, 360, 300))
        shelf.levels.append(Level(shelf, 3, 360, 300))
        shelf.levels.append(Level(shelf, 4, 360, 300))
        levelid_to_displaygoods_list = {
            2: [DisplayGoods(TestGoods('c2_1', 'c3_3', '21', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '22', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '23', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '24', 100, 80, 9, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '25', 100, 80, 8, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '26', 100, 80, 7, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '27', 100, 80, 6, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '28', 100, 40, 5, 0, 0))],
        }
        shelf.levels[2].display_goods_list = levelid_to_displaygoods_list[2]

        choose_goods_list = []

        area_manager = AreaManager(shelf, levelid_to_displaygoods_list, choose_goods_list)

        area_manager._first_born_areas()
        area_manager._second_combine_areas()
        area_manager._prepare_area_base_data()

        area_manager._prepare_area_calculate_data()
        area_manager._print_choose_goods_info()
        area_manager._arrange_areas()

        candidate_shelf_list = area_manager._generate_all_area_candidate()

        self.assertEqual(len(candidate_shelf_list), 1)
        # for shelf_list in candidate_shelf_list:
        #     print(shelf_list)

        best_candidate_shelf = area_manager.calculate_best_candidate_shelf(candidate_shelf_list)
        level_to_display_goods_name_str = get_level_to_display_goods_name(best_candidate_shelf)

        self.assertEqual(level_to_display_goods_name_str[0], 'null,')
        self.assertEqual(level_to_display_goods_name_str[1], 'null,')
        self.assertEqual(level_to_display_goods_name_str[2], '21,22,23,24,25,26,27,28,')
        print(shelf)
        print(best_candidate_shelf)

def get_level_to_display_goods_name(shelf):
    level_to_display_goods_name_str = {}
    for level in shelf.levels:
        display_goods_name_str = ''
        for display_goods in level.display_goods_list:
            for i in range(display_goods.face_num):
                display_goods_name_str += display_goods.goods_data.goods_name
                display_goods_name_str += ','

        level_to_display_goods_name_str[level.level_id] = display_goods_name_str

    return level_to_display_goods_name_str
