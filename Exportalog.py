import subprocess
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QLineEdit, QLabel
from PyQt5.QtCore import QThread, pyqtSignal


class ExtractionThread(QThread):
	finished = pyqtSignal()
	error_occurred = pyqtSignal(str)

	def __init__(self, command):
		super().__init__()
		self.command = command

	def run(self):
		process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		process.wait()

		if process.returncode != 0:
			self.error_occurred.emit(process.stderr.read().decode())
		else:
			self.finished.emit()


class LogExtractor(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Extrator de Tabelas de Log Sybase 12")
		self.setGeometry(100, 100, 400, 300)

		self.file_path = ""
		self.table_name = ""

		self.init_ui()

	def init_ui(self):
		self.log_label = QLabel("Nenhum log selecionado.", self)
		self.log_label.setGeometry(50, 20, 500, 30)

		self.btn_browse = QPushButton("Procurar Log", self)
		self.btn_browse.setGeometry(50, 50, 150, 30)
		self.btn_browse.clicked.connect(self.browse_log)

		self.btn_extract = QPushButton("Extrair Tabela", self)
		self.btn_extract.setGeometry(50, 150, 150, 30)
		self.btn_extract.clicked.connect(self.extract_table)
		self.btn_extract.setEnabled(False)

		self.progress_label = QLabel("", self)
		self.progress_label.setGeometry(50, 200, 300, 30)

		self.table_name_label = QLabel("Nome da Tabela:", self)
		self.table_name_label.setGeometry(50, 100, 100, 30)

		self.table_name_input = QLineEdit(self)
		self.table_name_input.setGeometry(150, 100, 150, 30)

	def update_log_label(self, path):
		self.log_label.setText(f"Log selecionado: {path}")

	def browse_log(self):
		options = QFileDialog.Options()
		file_path, _ = QFileDialog.getOpenFileName(self, "Procurar Log", "", "Log Files (*.log)", options=options)
		if file_path:
			self.file_path = file_path
			self.btn_extract.setEnabled(True)
			self.update_log_label(self.file_path)

	def extract_table(self):
		if not self.file_path:
			QMessageBox.warning(self, "Log Não Selecionado", "Por favor, selecione um log.")
			return

		self.table_name = self.table_name_input.text()
		if not self.table_name:
			QMessageBox.warning(self, "Nome da Tabela", "Por favor, digite o nome da tabela.")
			return

		output_path, _ = QFileDialog.getSaveFileName(self, "Salvar Log da Tabela", "", "Text Files (*.txt)")
		if output_path:
			self.progress_label.setText("Extraindo, aguarde...")
			self.btn_browse.setEnabled(False)
			self.btn_extract.setEnabled(False)
			self.table_name_input.setEnabled(False)

			os.chdir("C:\\Program Files\\SQL Anywhere 12\\Bin64")
			command = f'dbtran -s -r "{self.file_path}" -it dba.{self.table_name} -n "{output_path}"'
			self.extraction_thread = ExtractionThread(command)
			self.extraction_thread.finished.connect(self.extraction_finished)
			self.extraction_thread.error_occurred.connect(self.extraction_error)
			self.extraction_thread.start()

	def extraction_finished(self):
		self.progress_label.setText("")
		self.btn_browse.setEnabled(True)
		self.btn_extract.setEnabled(True)
		self.table_name_input.setEnabled(True)
		QMessageBox.information(self, "Extração Concluída", "Extração concluída com sucesso.")

	def extraction_error(self, error_message):
		self.progress_label.setText("")
		self.btn_browse.setEnabled(True)
		self.btn_extract.setEnabled(True)
		self.table_name_input.setEnabled(True)
		QMessageBox.warning(self, "Erro", f"Ocorreu um erro durante a extração: {error_message}")


if __name__ == "__main__":
	app = QApplication([])
	window = LogExtractor()
	window.show()
	app.exec_()