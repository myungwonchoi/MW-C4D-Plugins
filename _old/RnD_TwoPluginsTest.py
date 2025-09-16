# Python 3.x
import c4d
from c4d import plugins
from c4d import bitmaps
import os

CMD_PLUGIN_ID = 1000001
TRIGGER_PLUGIN_ID = 1000002

kBaseMessageID = c4d.ID_TREEVIEW_FIRST_NEW_ID
kTriggerMessageID = kBaseMessageID + 1
kAnotherTriggerMessageID = kBaseMessageID + 2
# ... etc

# =============== CommandData class =============

class TestCommandData(c4d.plugins.CommandData):
	
	def Execute(self, doc):
		return True
		
	def ExecuteSubID(self, doc, subid):
		print(subid)
		if subid == kTriggerMessageID:
			# we got triggered .. do something
			print("TestCommandData was triggered for", subid)
		return True

class TriggerCommandData(c4d.plugins.CommandData):
	
	def Execute(self, doc):
		print("TriggerCommandData calls TestCommandData.ExecuteSubID with value", kTriggerMessageID)
		c4d.CallCommand(CMD_PLUGIN_ID, kTriggerMessageID)
		return True

# =============== Main =============

def PluginMain():
	bmp = c4d.bitmaps.BaseBitmap()
	dir, file = os.path.split(__file__)
	fn = os.path.join(dir, "res", "test.png")
	bmp.InitWith(fn)
	plugins.RegisterCommandPlugin(
		id=CMD_PLUGIN_ID,
		str="TestCommand",
		info=0,
		icon=bmp, 
		help="TestCommand",
		dat=TestCommandData())
	plugins.RegisterCommandPlugin(
		id=TRIGGER_PLUGIN_ID,
		str="TriggerCommand",
		info=0,
		icon=bmp, 
		help="TriggerCommand",
		dat=TriggerCommandData())

	return

if __name__ == "__main__":
	PluginMain()
