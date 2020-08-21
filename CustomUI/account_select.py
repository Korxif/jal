from PySide2.QtCore import Qt, Signal, Property
from PySide2.QtWidgets import QPushButton, QComboBox, QMenu
from PySide2.QtSql import QSqlTableModel
from DB.helpers import get_base_currency_name

from CustomUI.reference_data import ReferenceDataDialog, ReferenceBoolDelegate, \
    ReferenceLookupDelegate, ReferenceTimestampDelegate


########################################################################################################################
#  UI Button to choose accounts
########################################################################################################################
class AccountButton(QPushButton):
    changed = Signal(int)

    def __init__(self, parent):
        QPushButton.__init__(self, parent)
        self.p_account_id = 0
        self.setText("ANY")

        self.Menu = QMenu()
        self.Menu.addAction('Choose account', self.ChooseAccount)
        self.Menu.addAction('Any account', self.ClearAccount)
        self.setMenu(self.Menu)

        self.dialog = None

    def getId(self):
        return self.p_account_id

    def setId(self, account_id):
        self.p_account_id = account_id

    account_id = Property(int, getId, setId, notify=changed)

    @Signal
    def account_id_changed(self):
        pass

    def init_db(self, db):
        self.dialog = ReferenceDataDialog(db, "accounts",
                            [("id", None, 0, None, None),
                             ("name", "Name", -1, Qt.AscendingOrder, None),
                             ("type_id", None, 0, None, None),
                             ("currency_id", "Currency", None, None, ReferenceLookupDelegate),
                             ("active", "Act", 32, None, ReferenceBoolDelegate),
                             ("number", "Account #", None, None, None),
                             ("reconciled_on", "Reconciled @", self.fontMetrics().width("00/00/0000 00:00:00") * 1.1,
                              None, ReferenceTimestampDelegate),
                             ("organization_id", "Bank", None, None, ReferenceLookupDelegate)],
                            title="Assets", search_field="full_name", toggle=("active", "Show inactive"),
                            relations=[("type_id", "account_types", "id", "name", "Account type:"),
                                       ("currency_id", "currencies", "id", "name", None),
                                       ("organization_id", "agents", "id", "name", None)])
        self.setText(self.dialog.SelectedName)

    def ChooseAccount(self):
        ref_point = self.mapToGlobal(self.geometry().bottomLeft())
        self.dialog.setGeometry(ref_point.x(), ref_point.y(), self.dialog.width(), self.dialog.height())
        self.dialog.setFilter()
        res = self.dialog.exec_()
        if res:
            self.account_id = self.dialog.selected_id
            self.setText(self.dialog.SelectedName)
            self.changed.emit(self.account_id)

    def ClearAccount(self):
        if self.account_id:
            self.account_id = 0
            self.setText("ANY")
            self.changed.emit(self.account_id)


class CurrencyCombo(QComboBox):
    def __init__(self, parent):
        QComboBox.__init__(self, parent)
        self.model = None

    def init_db(self, db):
        self.model = QSqlTableModel(db=db)
        self.model.setTable('currencies')
        self.model.select()
        self.setModel(self.model)
        self.setModelColumn(1)
        self.setCurrentIndex(self.findText(get_base_currency_name(db)))

    def selected_currency(self):
        return self.model.record(self.currentIndex()).value("id")

    def selected_currency_name(self):
        return self.model.record(self.currentIndex()).value("name")