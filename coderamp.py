from scaleway import delete_all_codeboxes, new_instance
from install import setup_coderamp

delete_all_codeboxes()
ip = new_instance('test1')
setup_coderamp("51.159.164.94")