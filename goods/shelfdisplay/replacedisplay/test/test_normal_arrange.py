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

    def test_bottom_level(self):

        shelf = Shelf(1, 1800, 600, 300)
        shelf.levels.append(Level(shelf, 0, 360, 300))
        shelf.levels.append(Level(shelf, 1, 360, 300))
        shelf.levels.append(Level(shelf, 2, 360, 300))
        shelf.levels.append(Level(shelf, 3, 360, 300))
        shelf.levels.append(Level(shelf, 4, 360, 300))
        levelid_to_displaygoods_list = {
            0: [DisplayGoods(TestGoods('c2_1', 'c3_1', '1', 200, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '2', 200, 80, 9, 0, 0), face_num=2),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '3', 200, 40, 8, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '4', 200, 40, 7, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_2', '5', 200, 20, 6, 0, 0), face_num=2),
                DisplayGoods(TestGoods('c2_1', 'c3_2', '6', 200, 40, 5, 0, 0), face_num=3),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '7', 150, 40, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '8', 150, 40, 10, 0, 0))],
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
                DisplayGoods(TestGoods('c2_1', 'c3_4', '24', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '25', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '26', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '27', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '28', 100, 40, 10, 0, 0))],
            3: [DisplayGoods(TestGoods('c2_2', 'c3_6', '38', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '37', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '36', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '35', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '34', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '33', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '32', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '31', 100, 40, 10, 0, 0))],
            4: [DisplayGoods(TestGoods('c2_2', 'c3_6', '41', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '42', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '43', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '44', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '45', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '46', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '47', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_8', '48', 100, 40, 10, 0, 0))],
        }
        shelf.levels[0].display_goods_list = levelid_to_displaygoods_list[0]
        shelf.levels[1].display_goods_list = levelid_to_displaygoods_list[1]
        shelf.levels[2].display_goods_list = levelid_to_displaygoods_list[2]
        shelf.levels[3].display_goods_list = levelid_to_displaygoods_list[3]
        shelf.levels[4].display_goods_list = levelid_to_displaygoods_list[4]

        choose_goods_list = [
            TestGoods('c2_1', 'c3_1', '101', 100, 80, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_1', '102', 110, 80, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_1', '103', 120, 160, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_1', '4', 100, 40, 7, 2, 0),  # 下架
            TestGoods('c2_1', 'c3_2', '5', 100, 40, 6, 2, 0),  # 下架
        ]

        area_manager = AreaManager(shelf, levelid_to_displaygoods_list, choose_goods_list)

        area_manager._first_born_areas()
        area_manager._second_combine_areas()
        area_manager._prepare_area_base_data()
        area_manager._prepare_area_calculate_data()
        area_manager._arrange_areas()
        area_manager._print_choose_goods_info()

        self.assertGreater(len(area_manager.area_list[0].candidate_display_goods_list_list), 2)
        self.assertEqual(area_manager.area_list[1].candidate_display_goods_list_list, None)
        self.assertEqual(area_manager.area_list[2].candidate_display_goods_list_list, None)
        self.assertEqual(area_manager.area_list[3].candidate_display_goods_list_list, None)

        best_candidate_shelf = area_manager.arrange_goods()
        level_to_display_goods_name_str = get_level_to_display_goods_name(best_candidate_shelf)

        self.assertEqual(level_to_display_goods_name_str[0], '1,2,103,102,101,7,8,')
        self.assertEqual(level_to_display_goods_name_str[1], '11,12,13,14,15,16,17,18,')
        self.assertEqual(level_to_display_goods_name_str[2], '21,22,23,24,25,26,27,28,')
        self.assertEqual(level_to_display_goods_name_str[3], '31,32,33,34,35,36,37,38,')
        self.assertEqual(level_to_display_goods_name_str[4], '41,42,43,44,45,46,47,48,')
        print(best_candidate_shelf)


    def test_area_not_enough(self):

        shelf = Shelf(1, 1800, 600, 300)
        shelf.levels.append(Level(shelf, 0, 360, 300))
        shelf.levels.append(Level(shelf, 1, 360, 300))
        shelf.levels.append(Level(shelf, 2, 360, 300))
        shelf.levels.append(Level(shelf, 3, 360, 300))
        shelf.levels.append(Level(shelf, 4, 360, 300))
        levelid_to_displaygoods_list = {
            0: [DisplayGoods(TestGoods('c2_1', 'c3_1', '1', 200, 40, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '2', 200, 40, 9, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '3', 200, 40, 8, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '4', 200, 40, 7, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_2', '5', 200, 20, 6, 0, 0), face_num=2),
                DisplayGoods(TestGoods('c2_1', 'c3_2', '6', 200, 40, 5, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '7', 150, 160, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '8', 150, 80, 10, 0, 0))],
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
                DisplayGoods(TestGoods('c2_1', 'c3_4', '24', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '25', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '26', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '27', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '28', 100, 40, 10, 0, 0))],
            3: [DisplayGoods(TestGoods('c2_2', 'c3_6', '38', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '37', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '36', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '35', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '34', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '33', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '32', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '31', 100, 40, 10, 0, 0))],
            4: [DisplayGoods(TestGoods('c2_2', 'c3_6', '41', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '42', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '43', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '44', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '45', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '46', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '47', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_8', '48', 100, 40, 10, 0, 0))],
        }
        shelf.levels[0].display_goods_list = levelid_to_displaygoods_list[0]
        shelf.levels[1].display_goods_list = levelid_to_displaygoods_list[1]
        shelf.levels[2].display_goods_list = levelid_to_displaygoods_list[2]
        shelf.levels[3].display_goods_list = levelid_to_displaygoods_list[3]
        shelf.levels[4].display_goods_list = levelid_to_displaygoods_list[4]

        choose_goods_list = [
            TestGoods('c2_1', 'c3_1', '101', 100, 80, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_1', '102', 110, 80, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_1', '103', 120, 160, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_1', '4', 100, 40, 7, 2, 0),  # 下架
            TestGoods('c2_1', 'c3_2', '5', 100, 40, 6, 2, 0),  # 下架
        ]

        area_manager = AreaManager(shelf, levelid_to_displaygoods_list, choose_goods_list)

        area_manager._first_born_areas()
        area_manager._second_combine_areas()
        area_manager._prepare_area_base_data()
        area_manager._prepare_area_calculate_data()
        area_manager._arrange_areas()
        area_manager._print_choose_goods_info()

        self.assertEqual(len(area_manager.area_list[0].candidate_display_goods_list_list), 1)
        self.assertEqual(area_manager.area_list[1].candidate_display_goods_list_list, None)
        self.assertEqual(area_manager.area_list[2].candidate_display_goods_list_list, None)
        self.assertEqual(area_manager.area_list[3].candidate_display_goods_list_list, None)

        best_candidate_shelf = area_manager.arrange_goods()
        level_to_display_goods_name_str = get_level_to_display_goods_name(best_candidate_shelf)

        self.assertEqual(level_to_display_goods_name_str[0], '103,102,101,7,8,')
        self.assertEqual(level_to_display_goods_name_str[1], '11,12,13,14,15,16,17,18,')
        self.assertEqual(level_to_display_goods_name_str[2], '21,22,23,24,25,26,27,28,')
        self.assertEqual(level_to_display_goods_name_str[3], '31,32,33,34,35,36,37,38,')
        self.assertEqual(level_to_display_goods_name_str[4], '41,42,43,44,45,46,47,48,')
        print(best_candidate_shelf)

    def test_bottom_middle_level(self):

        shelf = Shelf(1, 1800, 600, 300)
        shelf.levels.append(Level(shelf, 0, 360, 300))
        shelf.levels.append(Level(shelf, 1, 360, 300))
        shelf.levels.append(Level(shelf, 2, 360, 300))
        shelf.levels.append(Level(shelf, 3, 360, 300))
        shelf.levels.append(Level(shelf, 4, 360, 300))
        levelid_to_displaygoods_list = {
            0: [DisplayGoods(TestGoods('c2_1', 'c3_1', '1', 200, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '2', 200, 80, 9, 0, 0), face_num=2),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '3', 200, 40, 8, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '4', 200, 40, 7, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_2', '5', 200, 20, 6, 0, 0), face_num=2),
                DisplayGoods(TestGoods('c2_1', 'c3_2', '6', 200, 40, 5, 0, 0), face_num=3),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '7', 150, 40, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '8', 150, 40, 10, 0, 0))],
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
            3: [DisplayGoods(TestGoods('c2_2', 'c3_6', '38', 100, 40, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '37', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '36', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '35', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '34', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '33', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '32', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '31', 100, 80, 4, 0, 0))],
            4: [DisplayGoods(TestGoods('c2_2', 'c3_6', '41', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '42', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '43', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '44', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '45', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '46', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '47', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_8', '48', 100, 40, 10, 0, 0))],
        }
        shelf.levels[0].display_goods_list = levelid_to_displaygoods_list[0]
        shelf.levels[1].display_goods_list = levelid_to_displaygoods_list[1]
        shelf.levels[2].display_goods_list = levelid_to_displaygoods_list[2]
        shelf.levels[3].display_goods_list = levelid_to_displaygoods_list[3]
        shelf.levels[4].display_goods_list = levelid_to_displaygoods_list[4]

        choose_goods_list = [
            TestGoods('c2_1', 'c3_1', '101', 100, 80, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_4', '102', 100, 80, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_5', '103', 100, 160, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_1', '4', 100, 40, 7, 2, 0),  # 下架
            TestGoods('c2_1', 'c3_4', '25', 100, 40, 8, 2, 0),  # 下架
        ]

        area_manager = AreaManager(shelf, levelid_to_displaygoods_list, choose_goods_list)

        area_manager._first_born_areas()
        area_manager._second_combine_areas()
        area_manager._prepare_area_base_data()
        area_manager._prepare_area_calculate_data()
        area_manager._arrange_areas()
        area_manager._print_choose_goods_info()

        self.assertEqual(len(area_manager.area_list[0].candidate_display_goods_list_list), 4)
        self.assertEqual(area_manager.area_list[1].candidate_display_goods_list_list, None)
        self.assertGreater(len(area_manager.area_list[2].candidate_display_goods_list_list), 2)
        self.assertEqual(area_manager.area_list[3].candidate_display_goods_list_list, None)

        best_candidate_shelf = area_manager.arrange_goods()
        level_to_display_goods_name_str = get_level_to_display_goods_name(best_candidate_shelf)

        self.assertEqual(level_to_display_goods_name_str[0], '1,2,2,3,101,5,5,6,6,7,8,')
        self.assertEqual(level_to_display_goods_name_str[1], '11,12,13,14,15,16,17,18,')
        self.assertEqual(level_to_display_goods_name_str[2], '21,22,23,24,26,103,')
        self.assertEqual(level_to_display_goods_name_str[3], '102,32,33,34,35,36,37,38,')
        self.assertEqual(level_to_display_goods_name_str[4], '41,42,43,44,45,46,47,48,')
        print(shelf)
        print(best_candidate_shelf)

    def test_no_choose_goods(self):
        shelf = Shelf(1, 1800, 600, 300)
        shelf.levels.append(Level(shelf, 0, 360, 300))
        shelf.levels.append(Level(shelf, 1, 360, 300))
        shelf.levels.append(Level(shelf, 2, 360, 300))
        shelf.levels.append(Level(shelf, 3, 360, 300))
        shelf.levels.append(Level(shelf, 4, 360, 300))
        levelid_to_displaygoods_list = {
            0: [DisplayGoods(TestGoods('c2_1', 'c3_1', '1', 200, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '2', 200, 80, 9, 0, 0), face_num=2),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '3', 200, 40, 8, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_1', '4', 200, 40, 7, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_2', '5', 200, 20, 6, 0, 0), face_num=2),
                DisplayGoods(TestGoods('c2_1', 'c3_2', '6', 200, 40, 5, 0, 0), face_num=3),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '7', 150, 40, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '8', 150, 40, 10, 0, 0))],
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
            3: [DisplayGoods(TestGoods('c2_2', 'c3_6', '38', 100, 40, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '37', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '36', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '35', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '34', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '33', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '32', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '31', 100, 80, 4, 0, 0))],
            4: [DisplayGoods(TestGoods('c2_2', 'c3_6', '41', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '42', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '43', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '44', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '45', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '46', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_7', '47', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_8', '48', 100, 40, 10, 0, 0))],
        }
        shelf.levels[0].display_goods_list = levelid_to_displaygoods_list[0]
        shelf.levels[1].display_goods_list = levelid_to_displaygoods_list[1]
        shelf.levels[2].display_goods_list = levelid_to_displaygoods_list[2]
        shelf.levels[3].display_goods_list = levelid_to_displaygoods_list[3]
        shelf.levels[4].display_goods_list = levelid_to_displaygoods_list[4]

        choose_goods_list = []

        area_manager = AreaManager(shelf, levelid_to_displaygoods_list, choose_goods_list)

        area_manager._first_born_areas()
        area_manager._second_combine_areas()
        area_manager._prepare_area_base_data()

        area_manager._prepare_area_calculate_data()
        area_manager._arrange_areas()
        area_manager._print_choose_goods_info()

        best_candidate_shelf = area_manager.arrange_goods()
        level_to_display_goods_name_str = get_level_to_display_goods_name(best_candidate_shelf)

        self.assertEqual(level_to_display_goods_name_str[0], '1,2,2,3,4,5,5,6,6,6,7,8,')
        self.assertEqual(level_to_display_goods_name_str[1], '11,12,13,14,15,16,17,18,')
        self.assertEqual(level_to_display_goods_name_str[2], '21,22,23,24,25,26,27,28,')
        self.assertEqual(level_to_display_goods_name_str[3], '31,32,33,34,35,36,37,38,')
        self.assertEqual(level_to_display_goods_name_str[4], '41,42,43,44,45,46,47,48,')
        print(shelf)
        print(best_candidate_shelf)
