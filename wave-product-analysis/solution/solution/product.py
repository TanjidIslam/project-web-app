class ObjectProduct(object):
    def __init__(self, **entries):
        '''
        Convert dictionary into python object
        '''
        self.__dict__.update(entries)


class Product(object):
    def __init__(self, _id, url, name, price, description, is_sold, is_bought, income_account,
                 expense_account, active, default_sales_taxes, date_created, date_modified):
        '''
        Product object, was not used for this case, but can be used to populate/post
        '''
        self.id = _id
        self.url = url
        self.name = name
        self.price = price
        self.description = description
        self.is_sold = is_sold
        self.is_bought = is_bought
        self.income_account = income_account
        self.expense_account = expense_account
        self.active = active
        self.default_sales_tax = default_sales_taxes
        self.date_created = date_created
        self.date_modified = date_modified
