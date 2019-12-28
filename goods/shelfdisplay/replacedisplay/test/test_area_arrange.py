import unittest
from goods.shelfdisplay.replacedisplay.display_object import Shelf, Level, DisplayGoods
from goods.shelfdisplay.replacedisplay.area_arrange import AreaManager

class TestGoods:
    def __init__(self, category2, category3, goods_name, height, width, psd_amount, goods_role, ranking):
        self.category2 = category2
        self.category3 = category3
        self.goods_name = goods_name
        self.height = height
        self.width = width
        self.psd_amount = psd_amount
        self.goods_role = goods_role
        self.ranking = ranking

    def equal(self, another_goods):
        if another_goods is not None:
            return self.goods_name == another_goods.goods_name
        return False

    def __str__(self):
        return self.goods_name


class Test1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
            1: [DisplayGoods(TestGoods('c2_1', 'c3_3', '11', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '12', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '13', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '14', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '15', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '16', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '17', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '18', 150, 40, 10, 0, 0))],
            2: [DisplayGoods(TestGoods('c2_1', 'c3_3', '21', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_3', '22', 150, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '23', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '24', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '25', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_4', '26', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '27', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '28', 100, 40, 10, 0, 0))],
            3: [DisplayGoods(TestGoods('c2_1', 'c3_5', '31', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_1', 'c3_5', '32', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '33', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '34', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '35', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '36', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '37', 100, 80, 10, 0, 0)),
                DisplayGoods(TestGoods('c2_2', 'c3_6', '38', 100, 40, 10, 0, 0))],
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

        cls.shelf = shelf
        cls.levelid_to_displaygoods_list = levelid_to_displaygoods_list

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_bottom_level(self):

        choose_goods_list = [
            TestGoods('c2_1', 'c3_1', '101', 100, 80, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_1', '102', 100, 80, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_1', '103', 100, 160, 20, 1, 0),  # 上架
            TestGoods('c2_1', 'c3_1', '4', 100, 40, 7, 2, 0),  # 下架
            TestGoods('c2_1', 'c3_2', '5', 100, 40, 6, 2, 0),  # 下架
        ]

        area_manager = AreaManager(self.shelf, self.levelid_to_displaygoods_list, choose_goods_list)

        area_manager._first_born_areas()

        self.assertEqual(len(area_manager.area_list), 8)

        self.assertEqual(len(area_manager.area_list[0].child_area_list), 1)
        self.assertEqual(area_manager.area_list[0].child_area_list[0].level_id, 0)
        self.assertEqual(len(area_manager.area_list[0].child_area_list[0].display_goods_list), 4)

        self.assertEqual(len(area_manager.area_list[1].child_area_list), 1)
        self.assertEqual(area_manager.area_list[1].child_area_list[0].level_id, 0)
        self.assertEqual(len(area_manager.area_list[1].child_area_list[0].display_goods_list), 2)

        self.assertEqual(len(area_manager.area_list[2].child_area_list), 3)
        self.assertEqual(area_manager.area_list[2].child_area_list[0].level_id, 0)
        self.assertEqual(len(area_manager.area_list[2].child_area_list[0].display_goods_list), 2)
        self.assertEqual(area_manager.area_list[2].child_area_list[1].level_id, 1)
        self.assertEqual(len(area_manager.area_list[2].child_area_list[1].display_goods_list), 8)
        self.assertEqual(area_manager.area_list[2].child_area_list[2].level_id, 2)
        self.assertEqual(len(area_manager.area_list[2].child_area_list[2].display_goods_list), 2)

        self.assertEqual(len(area_manager.area_list[3].child_area_list), 1)
        self.assertEqual(area_manager.area_list[3].child_area_list[0].level_id, 2)
        self.assertEqual(len(area_manager.area_list[3].child_area_list[0].display_goods_list), 4)

        self.assertEqual(len(area_manager.area_list[4].child_area_list), 2)
        self.assertEqual(area_manager.area_list[4].child_area_list[0].level_id, 2)
        self.assertEqual(len(area_manager.area_list[4].child_area_list[0].display_goods_list), 2)
        self.assertEqual(area_manager.area_list[4].child_area_list[1].level_id, 3)
        self.assertEqual(len(area_manager.area_list[4].child_area_list[1].display_goods_list), 2)

        self.assertEqual(len(area_manager.area_list[5].child_area_list), 2)
        self.assertEqual(area_manager.area_list[5].child_area_list[0].level_id, 3)
        self.assertEqual(len(area_manager.area_list[5].child_area_list[0].display_goods_list), 6)
        self.assertEqual(area_manager.area_list[5].child_area_list[1].level_id, 4)
        self.assertEqual(len(area_manager.area_list[5].child_area_list[1].display_goods_list), 2)

        self.assertEqual(len(area_manager.area_list[6].child_area_list), 1)
        self.assertEqual(area_manager.area_list[6].child_area_list[0].level_id, 4)
        self.assertEqual(len(area_manager.area_list[6].child_area_list[0].display_goods_list), 5)

        self.assertEqual(len(area_manager.area_list[7].child_area_list), 1)
        self.assertEqual(area_manager.area_list[7].child_area_list[0].level_id, 4)
        self.assertEqual(len(area_manager.area_list[7].child_area_list[0].display_goods_list), 1)

        # for area in area_manager.area_list:
        #     print(area)

        area_manager._second_combine_areas()
        self.assertEqual(len(area_manager.area_list), 4)

        self.assertEqual(len(area_manager.area_list[0].child_area_list), 2)
        self.assertEqual(len(area_manager.area_list[0].child_area_list[0].display_goods_list), 4)
        self.assertEqual(len(area_manager.area_list[0].child_area_list[1].display_goods_list), 2)

        self.assertEqual(len(area_manager.area_list[1].child_area_list), 3)
        self.assertEqual(len(area_manager.area_list[1].child_area_list[0].display_goods_list), 2)
        self.assertEqual(len(area_manager.area_list[1].child_area_list[1].display_goods_list), 8)
        self.assertEqual(len(area_manager.area_list[1].child_area_list[2].display_goods_list), 2)

        self.assertEqual(len(area_manager.area_list[2].child_area_list), 3)
        self.assertEqual(len(area_manager.area_list[2].child_area_list[0].display_goods_list), 4)
        self.assertEqual(len(area_manager.area_list[2].child_area_list[1].display_goods_list), 2)
        self.assertEqual(len(area_manager.area_list[2].child_area_list[2].display_goods_list), 2)

        self.assertEqual(len(area_manager.area_list[3].child_area_list), 4)
        self.assertEqual(len(area_manager.area_list[3].child_area_list[0].display_goods_list), 6)
        self.assertEqual(len(area_manager.area_list[3].child_area_list[1].display_goods_list), 2)
        self.assertEqual(len(area_manager.area_list[3].child_area_list[2].display_goods_list), 5)
        self.assertEqual(len(area_manager.area_list[3].child_area_list[3].display_goods_list), 1)

        # print('\n')
        for area in area_manager.area_list:
            print(area)

        area_manager._prepare_area_base_data()
        self.assertEqual(len(area_manager.area_list[0].choose_goods_list), 5)
        self.assertEqual(len(area_manager.area_list[1].choose_goods_list), 0)
        self.assertEqual(len(area_manager.area_list[2].choose_goods_list), 0)
        self.assertEqual(len(area_manager.area_list[3].choose_goods_list), 0)

        self.assertEqual(len(area_manager.area_list[0].up_choose_goods_list), 3)
        self.assertEqual(len(area_manager.area_list[0].down_display_goods_list), 2)
        self.assertEqual(len(area_manager.down_display_goods_list), 2)
        self.assertEqual(len(area_manager.area_list[0].child_area_list[0].down_display_goods_list), 1)
        self.assertEqual(len(area_manager.area_list[0].child_area_list[1].down_display_goods_list), 1)
        self.assertEqual(area_manager.area_list[0].levelid_to_goods_width[0], 480)
        self.assertEqual(area_manager.area_list[0].levelid_to_remain_width[0], int(480 / 600 * 40))
        self.assertEqual(area_manager.area_list[1].levelid_to_goods_width[0], 80)
        self.assertEqual(area_manager.area_list[1].levelid_to_remain_width[0], int(80 / 600 * 40))

        area_manager._prepare_area_calculate_data()
        self.assertEqual(len(area_manager.area_list[0].display_goods_to_reduce_face_num), 2)
        self.assertEqual(area_manager.area_list[0].display_goods_to_reduce_face_num[self.levelid_to_displaygoods_list[0][1]], 1)
        self.assertEqual(area_manager.area_list[0].display_goods_to_reduce_face_num[self.levelid_to_displaygoods_list[0][5]], 2)
        self.assertEqual(len(area_manager.area_list[0].second_down_display_goods_list), 2)
        self.assertEqual(area_manager.area_list[0].second_down_display_goods_list[0], self.levelid_to_displaygoods_list[0][5])
        self.assertEqual(area_manager.area_list[0].second_down_display_goods_list[1], self.levelid_to_displaygoods_list[0][2])
        self.assertEqual(len(area_manager.down_display_goods_list), 4)

        print('\n')
        for area in area_manager.area_list:
            print(area)
        area_manager._arrange_areas()

        self.assertEqual(area_manager.threshold, 100)
        self.assertEqual(len(area_manager.area_list[0].candidate_display_goods_list_list), 8)
        self.assertEqual(len(area_manager.area_list[1].candidate_display_goods_list_list), 1)
        self.assertEqual(len(area_manager.area_list[2].candidate_display_goods_list_list), 1)
        self.assertEqual(len(area_manager.area_list[3].candidate_display_goods_list_list), 1)

        candidate_shelf_list = area_manager._generate_all_area_candidate()

        self.assertEqual(len(candidate_shelf_list), 8)

        best_candidate_shelf = area_manager.calculate_best_candidate_shelf(candidate_shelf_list)
        print(best_candidate_shelf)


if __name__ == '__main__':
    unittest.main()#运行所有的测试用例