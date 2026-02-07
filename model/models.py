import csv
from datetime import datetime

class PoliticianModel:
    def __init__(self):
        self.politicians_file = '../model/data/politicians.csv'
        self.campaigns_file = '../model/data/campaigns.csv'
        self.promises_file = '../model/data/promises.csv'
        self.updates_file = '../model/data/promise_updates.csv'

    def _read_csv(self, file_path):
        """Helper function สำหรับอ่านไฟล์ CSV ออกมาเป็น List ของ Dictionary"""
        data = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            return []
        return data

    def get_all_promises(self):
        """ดึงคำสัญญาทั้งหมด และเรียงตามวันที่ประกาศ (ล่าสุดขึ้นก่อน)"""
        promises = self._read_csv(self.promises_file)
        politicians = self._read_csv(self.politicians_file)
        
        for p in promises:
            pol = next((item for item in politicians if item["id"] == p["politician_id"]), None)
            p['politician_name'] = pol['name'] if pol else "ไม่ทราบชื่อ"
            p['party'] = pol['party'] if pol else "ไม่ระบุพรรค"
        return sorted(promises, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)

    def get_promise_by_id(self, promise_id):
        """ดึงรายละเอียดคำสัญญาหนึ่งรายการ"""
        promises = self.get_all_promises()
        return next((p for p in promises if p['id'] == promise_id), None)

    def get_updates_by_promise(self, promise_id):
        """ดึงประวัติการอัปเดตของคำสัญญานั้นๆ"""
        updates = self._read_csv(self.updates_file)
        return [u for u in updates if u['promise_id'] == promise_id]

    def get_promises_by_politician(self, politician_id):
        """ดึงคำสัญญาทั้งหมดของนักการเมืองแต่ละคน (Business Rule ข้อ 3)"""
        promises = self.get_all_promises()
        return [p for p in promises if p['politician_id'] == politician_id]

    def add_update(self, promise_id, detail):
        """บันทึกความคืบหน้าใหม่ (ต้องเช็คสถานะก่อน)"""
        promise = self.get_promise_by_id(promise_id)
        if promise and promise['status'] == "เงียบหาย":
            return False, "คำสัญญานี้ 'เงียบหาย' ไปแล้ว ไม่สามารถอัปเดตได้"

        new_update = {
            'promise_id': promise_id,
            'update_date': datetime.now().strftime('%Y-%m-%d'),
            'update_detail': detail
        }
        with open(self.updates_file, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['promise_id', 'update_date', 'update_detail'])
            writer.writerow(new_update)
            
        return True, "อัปเดตสำเร็จ"