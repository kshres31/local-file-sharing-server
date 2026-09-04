import tempfile, unittest
from pathlib import Path
from lan_drop.storage import Storage,safe_path

class StorageTests(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name); self.storage=Storage(self.root,max_bytes=5)
    def tearDown(self): self.temp.cleanup()
    def test_save_list_and_read(self):
        result=self.storage.save("hello.txt",b"hello"); self.assertEqual(result["size"],5); self.assertEqual(self.storage.list(),[{"name":"hello.txt","size":5}]); self.assertEqual(self.storage.read("hello.txt"),b"hello")
    def test_rejects_large_files(self):
        with self.assertRaisesRegex(ValueError,"too large"): self.storage.save("large.bin",b"123456")
    def test_does_not_overwrite(self):
        self.storage.save("same.txt",b"one")
        with self.assertRaises(FileExistsError): self.storage.save("same.txt",b"two")
    def test_blocks_parent_paths(self):
        with self.assertRaisesRegex(ValueError,"unsafe"): safe_path(self.root,"../secret.txt")

if __name__=="__main__": unittest.main()

