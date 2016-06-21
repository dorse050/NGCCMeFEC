#import helpers as h
import sys
import inspect
#sys.path.append('../')
import testSummary
import bridgeTests as bt
import client
import helpers
import Test
#from registers import registers



noCheckRegis = {
	"Unique_ID" :{
		"i2c_path" : [0x11, 0x04, 0,0,0],
		"address" : 0x50,
		"command" : [0x00],
		"sleep" : 0,
		"size" : 64,
		"RW" : 0,
#		"spaces" : 3 
	},
	"Temperature" : {
		"i2c_path" : [0x11, 0x05, 0,0,0],
		"address" : 0x40,
		"command" : [0xf3],
		"sleep" : 300,
		"size" : 16,
		"RW" : 0	
	},
	"Humidity" : {
		"i2c_path" : [0x11, 0x05, 0,0,0],
		"address" : 0x40,
		"command" : [0xf5],
		"sleep" : 300,
		"size" : 16,
		"RW" : 0	
	}
}

class testSuite:
    def __init__(self, webAddress, address):
        '''create a new test suite object... initialize bus and address'''
        self.b = client.webBus(webAddress, 0)
	self.outCard = testSummary.testSummary()
        self.a = address

	#Variables to clean up the long list of registers
	a = self.a
	b = self.b
	i = 100

	self.registers = {"ID_string" : bt.ID_string(b,a,i), "ID_string_cont" : bt.ID_string_cont(b,a,i),
    	"Ones" : bt.Ones(b,a,i), "Zeroes" : bt.Zeroes(b,a,i), "OnesZeroes" : bt.OnesZeroes(b,a,i),
    	"Firmware_Ver" : bt.Firmware_Ver(b,a,i), "Status" : bt.statusCheck(b,a,i),
	"Scratch" : bt.ScratchCheck(b,a,i), "ClockCnt" : bt.brdg_ClockCounter(b,a,i),
	"QIECount" : bt.RES_QIE_Counter(b,a,i), "WTECount" : bt.WTE_Counter(b,a,i),
	"BkPln_1" : bt.BkPln_Spare_1(b,a,i), "BkPln_2" : bt.BkPln_Spare_2(b,a,i), "BkPln_3" : bt.BkPln_Spare_3(b,a,i),
	"OrbHist_1" : bt.OrbHist_1(b,a,i),"OrbHist_2" : bt.OrbHist_2(b,a,i), "OrbHist_3" : bt.OrbHist_3(b,a,i),
	"OrbHist_4" : bt.OrbHist_4(b,a,i), "OrbHist_5" : bt.OrbHist_5(b,a,i)
	}

    def readWithCheck(self, registerName, iterations = 1):
        passes = 0
        register = registers[registerName]["address"]
        size = 4#registers[registerName]["size"] / 8
        check = registers[registerName]["expected"]

        for i in xrange(iterations):
            self.b.write(self.a, [register])
            self.b.read(self.a, size)
        r = self.b.sendBatch()
        for i in xrange(iterations * 2):
            if (i % 2 == 1) and (r[i] == check):
                passes += 1
        self.outCard.resultList[registerName] = (passes, iterations - passes) #(passes, fails)
	return (passes, iterations - passes)

    def readNoCheck(self, testName, iterations = 1):
	i2c_pathway = noCheckRegis[testName]["i2c_path"]
	register = noCheckRegis[testName]["address"]
	size = noCheckRegis[testName]["size"]/8
	command = noCheckRegis[testName]["command"]
	napTime = noCheckRegis[testName]["sleep"]
	
	for i in xrange(iterations):
		# Clear the backplane
		self.b.write(0x00,[0x06])

		self.b.write(self.a,i2c_pathway)
		self.b.write(register,command)
		if (napTime != 0):
			self.b.sleep(napTime)  #catching some z's
		self.b.read(register,size)

	r = self.b.sendBatch()
	# Remove the entries in r that contain no information
	new_r = []
	for i in r:
		if (i != '0' and i != 'None'):
			new_r.append(i)
	self.outCard.resultList[testName] = new_r
	if (testName == "Unique_ID"):
		new_r[0] = helpers.reverseBytes(new_r[0])
		new_r[0] = helpers.toHex(new_r[0])
	return new_r

    def runTests(self):
        for r in self.registers.keys():
		self.outCard.resultList[r] = self.registers[r].run()
	for r in noCheckRegis.keys():
	    self.readNoCheck(r, 1)
	self.outCard.printResults()
	print "\n\n"
	self.outCard.writeHumanLog()	
	self.outCard.writeMachineJson()

    def runSingleTest(self,key):
	if key in registers:
		yield self.readWithCheck(key, 100)
	elif key in noCheckRegis:
		yield self.readNoCheck(key, 1)

