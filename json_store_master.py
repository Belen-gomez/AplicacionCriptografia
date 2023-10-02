"""
Json store master
"""
import json
#from uc3m_logistics.exception.order_management_exception import OrderManagementException


class JsonStoreMaster:
    """
    Json store master
    """
    _FILE_PATH = ""
    _ID_FIELD = ""
    _data_list = []
    __ERROR_MESSAGE_PATH = "Wrong file or file path"
    __ERROR_JSON_DECODE = "JSON Decode Error - Wrong JSON Format"

    def __init__(self) -> None:
        self.load_store()
    
    
    def save_store(self) -> None:
        """
        save store
        """
        try:
            with open(self._FILE_PATH, "w", encoding="utf-8", newline="") as file:
                json.dump(self._data_list, file, indent=2)
        except FileNotFoundError as ex:
            #raise OrderManagementException(self.__ERROR_MESSAGE_PATH) from ex
            print("FileNotFoundError")

    def find_data(self, data_to_find: any) -> any:
        """
        find data
        """
        item_found = None
        for item in self._data_list:
            if item[self._ID_FIELD] == data_to_find:
                item_found = item
        return item_found

    def load_store(self) -> None:
        """
        load store
        """
        try:
            with open(self._FILE_PATH, "r", encoding="utf-8", newline="") as file:
                self._data_list = json.load(file)
        except FileNotFoundError:
            # file is not found , so  init my data_list
            self._data_list = []
        except json.JSONDecodeError as ex:
            #raise OrderManagementException(self.__ERROR_JSON_DECODE) from ex
            print("JSONDecodeError")

    def add_item(self, item: any) -> None:
        """
        add item
        """
        self.load_store()
        self._data_list.append(item.__dict__)
        self.save_store()
