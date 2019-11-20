from goods.sellgoods.salesquantity.bean import ai_sales_old
class Sales2LoadData:
    file_operator = 'tmp_sales_week.txt_'
    def load_data(self,train_x_date=None,train_y_date=None):
        if train_x_date != None:
            print (11)

    def load_x_from_localfile(self,train_x_date):
        xfile = self.file_operator+str(train_x_date)

        with open(xfile,'r') as f :
            lines = f.readlines()
            for line in lines:
                words = line.split(",")
