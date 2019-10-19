sql_params={
    #基于upc的训练sql
    "upc_data_sql":"(select sum(T2.t1_nums) as ai_nums,T2.t1_shop_id as ai_shop_id ,T3.upc as ai_upc,T2.t1_create_date as  ai_create_date,DATE_FORMAT( from_unixtime(unix_timestamp(DATE_FORMAT(T2.t1_create_date ,'%Y-%m-%d'))+24*3600),'%Y-%m-%d') as ai_next_date,DAYOFWEEK(DATE_FORMAT(from_unixtime(unix_timestamp(DATE_FORMAT(T2.t1_create_date ,'%Y-%m-%d'))-24*3600),'%Y-%m-%d')) as ai_week_date from ( "
                    "select sum(T1.nums) as t1_nums,T1.shop_id as t1_shop_id,T1.shop_goods_id,T1.create_date as t1_create_date  from "
		                "(select number nums,shop_id,shop_goods_id,DATE_FORMAT(create_time,'%Y-%m-%d') 	create_date from payment_detail "
                                "where shop_id is not null and goods_id is not null and number > 0 and create_time > '{0} 00:00:00' and create_time < '{1} 00:00:00' and "
				                "payment_id in ( "
                                    "select distinct(payment.id) from payment where payment.type != 50  and create_time > '{2} 00:00:00' and create_time < '{3} 00:00:00' "
											") "
                        ")  T1 "
		                "group by T1.shop_id,T1.shop_goods_id,T1.create_date) T2 "
                    "left join  shop_goods T3 on T2.t1_shop_id= T3.shop_id and T2.shop_goods_id = T3.id "
                    "where T3.upc != '' and  T3.upc != '0' "
                    "group by T2.t1_create_date,T2.t1_shop_id,T3.upc) tmp",


    "upc_data_sql_test":"(select sum(T2.t1_nums) as ai_nums,T2.t1_shop_id as ai_shop_id ,T3.upc as ai_upc,T2.t1_create_date as  ai_create_date,DATE_FORMAT( from_unixtime(unix_timestamp(DATE_FORMAT(T2.t1_create_date ,'%Y-%m-%d'))+24*3600),'%Y-%m-%d') as ai_next_date,DAYOFWEEK(DATE_FORMAT(from_unixtime(unix_timestamp(DATE_FORMAT(T2.t1_create_date ,'%Y-%m-%d'))-24*3600),'%Y-%m-%d')) as ai_week_date from ( "
                    "select sum(T1.nums) as t1_nums,T1.shop_id as t1_shop_id,T1.shop_goods_id,T1.create_date as t1_create_date  from "
		                "(select number nums,shop_id,shop_goods_id,DATE_FORMAT(create_time,'%Y-%m-%d') 	create_date from payment_detail "
                                "where shop_id is not null and goods_id is not null and number > 0 and create_time >= '{0} 00:00:00' and create_time < '{1} 00:00:00' and "
				                "payment_id in ( "
                                    "select distinct(payment.id) from payment where payment.type != 50  and create_time >= '{2} 00:00:00' and create_time < '{3} 00:00:00' "
											") "
                        ")  T1 "
		                "group by T1.shop_id,T1.shop_goods_id,T1.create_date) T2 "
                    "left join  shop_goods T3 on T2.t1_shop_id= T3.shop_id and T2.shop_goods_id = T3.id "
                    "where T3.upc != '' and  T3.upc != '0' "
                    "group by T2.t1_create_date,T2.t1_shop_id,T3.upc) tmp",

    "upc_data_sql_predict":"(select sum(T2.t1_nums) as ai_nums,T2.t1_shop_id as ai_shop_id ,T3.upc as ai_upc,T2.t1_create_date as  ai_create_date,DATE_FORMAT( from_unixtime(unix_timestamp(DATE_FORMAT(T2.t1_create_date ,'%Y-%m-%d'))+24*3600),'%Y-%m-%d') as ai_next_date,DAYOFWEEK(DATE_FORMAT(from_unixtime(unix_timestamp(DATE_FORMAT(T2.t1_create_date ,'%Y-%m-%d'))-24*3600),'%Y-%m-%d')) as ai_week_date from ( "
                    "select sum(T1.nums) as t1_nums,T1.shop_id as t1_shop_id,T1.shop_goods_id,T1.create_date as t1_create_date  from "
		                "(select number nums,shop_id,shop_goods_id,DATE_FORMAT(create_time,'%Y-%m-%d') 	create_date from payment_detail "
                                "where shop_id is not null and shop_id in {4} and goods_id is not null and number > 0 and create_time >= '{0} 00:00:00' and create_time < '{1} 00:00:00' and "
				                "payment_id in ( "
                                    "select distinct(payment.id) from payment where payment.type != 50  and create_time >= '{2} 00:00:00' and create_time < '{3} 00:00:00' "
											") "
                        ")  T1 "
		                "group by T1.shop_id,T1.shop_goods_id,T1.create_date) T2 "
                    "left join  shop_goods T3 on T2.t1_shop_id= T3.shop_id and T2.shop_goods_id = T3.id "
                    "where T3.upc != '' and  T3.upc != '0' "
                    "group by T2.t1_create_date,T2.t1_shop_id,T3.upc) tmp",

    ## stock from erp
    "get_stock_erp":"select stock,total_stock,upc,shop_id from shop_goods where shop_id = {0} ",

    ## min_sku max_sku from ucenter

    "tz_sums1":"select  shop_id,count(taizhang_id)  from sf_shop_taizhang  where  shop_id in (select id from uc_shop where mch_shop_code = {0} ) group by shop_id",

    # TODO 未添加 状态  后续需要加入执行状态
    "tz_sums2":"select sf_taizhang_display.taizhang_id,sf_taizhang_display.display_goods_info,sf_taizhang_display.display_shelf_info from sf_taizhang_display where sf_taizhang_display.taizhang_id in ("
                " select sf_shop_taizhang.taizhang_id  from sf_shop_taizhang  where  shop_id in (select uc_shop.id from uc_shop where uc_shop.mch_shop_code = {0} )"
                        ") ",

    "tz_shelf":"select id,length,height,depth from sf_shelf where id in {0}",
    "tz_upc":"select mch_goods_code,upc,width,height,depth  from uc_merchant_goods where mch_goods_code in {0}",
    # 读取销量数据表
    "sales_ai":"select shopid,upc,nextday_predict_sales from goods_ai_sales_goods where shopid in {0} and day = {1}",

}