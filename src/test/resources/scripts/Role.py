from PyConstants import Paths
from PyConstants import Codes
from PyConstants import CacheTimes
from PyBaseTest import BaseTest
from PyRequest import PyRequest
from Admin import Admin
import time

class Role(BaseTest):
    
    RoleUnpaid = 'unpaid'
    RoleUnlinked = 'unlinked'
    RoleUnconfirmed = 'unconfirmed'
    RoleUnaccepted = 'unaccepted'
    testEmailToken = "testingtoken"
    password = "testPassword123"
    
    def runTests(self, secondaryToken, lockedTargetToken1, lockedTargetToken2, paymentId1="sarin33133@yahoo.com", paymentId2="tjbarry@asu.edu", paymentId3="pyTest@test.com"):
        print("Running role tests")
        
        # testing value is much less
        #sleepTime = 60*3
        self.admin = Admin()
        sleepTime = 20
        self.secondaryAuthed = PyRequest(secondaryToken)
        self.lockedAuthed1 = PyRequest(lockedTargetToken1)
        self.lockedAuthed2 = PyRequest(lockedTargetToken2)
        expectedOverrideRoles = [Role.RoleUnaccepted]
        
        self.overrideRoles = {self.authed:list(expectedOverrideRoles),
                              self.targetAuthed:list(expectedOverrideRoles),
                              self.secondaryAuthed:list(expectedOverrideRoles),
                              self.lockedAuthed1:list(expectedOverrideRoles),
                              self.lockedAuthed2:list(expectedOverrideRoles)
                              }
        
        self.testOverrideRoles(self.authed, expectedOverrideRoles)
        self.testOverrideRoles(self.targetAuthed, expectedOverrideRoles)
        self.testOverrideRoles(self.secondaryAuthed, expectedOverrideRoles)
        self.testOverrideRoles(self.lockedAuthed1, expectedOverrideRoles)
        self.testOverrideRoles(self.lockedAuthed2, expectedOverrideRoles)

        self.testAccept(self.authed)
        self.testAccept(self.targetAuthed)
        self.testAccept(self.secondaryAuthed)
        self.testAccept(self.lockedAuthed1)
        self.testAccept(self.lockedAuthed2)
        
        self.testSendEmailConfirmation(self.authed)
        self.testSendEmailConfirmation(self.targetAuthed)
        self.testSendEmailConfirmation(self.secondaryAuthed)
        self.testSendEmailConfirmation(self.lockedAuthed1)
        self.testSendEmailConfirmation(self.lockedAuthed2)
        # wait until the email would be sent
        time.sleep(sleepTime)
        self.testHasEmailConfirmation(self.authed)
        self.testHasEmailConfirmation(self.targetAuthed)
        self.testHasEmailConfirmation(self.secondaryAuthed)
        self.testHasEmailConfirmation(self.lockedAuthed1)
        self.testHasEmailConfirmation(self.lockedAuthed2)
        
        self.testSendPaymentId(self.authed)
        self.testSendPaymentId(self.targetAuthed)
        self.testSendPaymentId(self.secondaryAuthed)
        self.testSendPaymentId(self.lockedAuthed1)
        self.testSendPaymentId(self.lockedAuthed2)
        time.sleep(sleepTime)
        
        self.testChangePaymentId(self.authed, paymentId1)
        self.testChangePaymentId(self.targetAuthed, paymentId2)
        self.testChangePaymentId(self.secondaryAuthed, paymentId3)
        self.testChangePaymentId(self.lockedAuthed1, paymentId3)
        self.testChangePaymentId(self.lockedAuthed2, paymentId3)
        
        self.testRemoveUnpaid(self.authed)
        self.testRemoveUnpaid(self.targetAuthed)
        self.testRemoveUnpaid(self.secondaryAuthed)
        self.testRemoveUnpaid(self.lockedAuthed1)
        self.testRemoveUnpaid(self.lockedAuthed2)
        
        self.testOverrideRoles(self.authed, [])
        self.testOverrideRoles(self.targetAuthed, [])
        self.testOverrideRoles(self.secondaryAuthed, [])
        self.testOverrideRoles(self.lockedAuthed1, [])
        self.testOverrideRoles(self.lockedAuthed2, [])
        
    def testAccept(self, authed):
        self.unauthed.expectResponse(Paths.USERS_ACCEPT, PyRequest.POST, None, self.expectedDenied)
        authed.expectResponse(Paths.USERS_ACCEPT, PyRequest.POST, None, self.expectedSuccess)

        if Role.RoleUnaccepted in self.overrideRoles[authed]:
            self.overrideRoles[authed].remove(Role.RoleUnaccepted)

    def testSendEmailConfirmation(self, authed):
        authed.expectResponse(Paths.CONFIRMATION_SEND, PyRequest.POST, None, self.expectedSuccess)
        self.unauthed.expectResponse(Paths.CONFIRMATION_SEND, PyRequest.POST, None, self.expectedDenied)
       
        
    def testHasEmailConfirmation(self, authed):
        self.unauthed.expectResponse(Paths.CONFIRMATION, PyRequest.POST, None, 
                                        self.expectedDenied, None, "emailToken=fakeToken")
        authed.expectResponse(Paths.CONFIRMATION, PyRequest.POST, None, 
                                        self.expectedInvalid, None, "emailToken=fakeToken")
        authed.expectResponse(Paths.CONFIRMATION, PyRequest.POST, None, 
                                        self.expectedSuccess, None, "emailToken=" + str(Role.testEmailToken))
        authed.expectResponse(Paths.CONFIRMATION, PyRequest.POST, None, 
                                        self.expectedInvalid, None, "emailToken=" + str(Role.testEmailToken))
        
        if Role.RoleUnconfirmed in self.overrideRoles[authed]:
            self.overrideRoles[authed].remove(Role.RoleUnconfirmed)
        
    def testRemoveUnpaid(self, authed):
        #data = authed.expectResponse(Paths.USERS_CURRENT, PyRequest.GET, None, self.unauthed.getDTOResponse())
        #username = data['dto']['username']['username']
        #self.admin.addCurrency(username, 1000)
        #if Role.RoleUnpaid in self.overrideRoles[authed]:
        #    self.overrideRoles[authed].remove(Role.RoleUnpaid)
        #self.testOverrideRoles(authed, self.overrideRoles[authed])
        None
        
    def testSendPaymentId(self, authed):
        self.unauthed.expectResponse(Paths.PAYMENT_CHANGE_REQUEST, PyRequest.POST, None, self.expectedDenied)
        authed.expectResponse(Paths.PAYMENT_CHANGE_REQUEST, PyRequest.POST, None, self.expectedSuccess)
        
    def testChangePaymentId(self, authed, paymentId):
        dto = {'paymentId':paymentId,
               'password':Role.password}
        self.unauthed.expectResponse(Paths.PAYMENT_CHANGE, PyRequest.POST, dto, self.expectedDenied)
        authed.expectResponse(Paths.PAYMENT_CHANGE, PyRequest.POST, dto, self.expectedInvalid)
        authed.expectResponse(Paths.PAYMENT_CHANGE, PyRequest.POST, dto, self.expectedInvalid, None, "emailToken=fakeToken")
        authed.expectResponse(Paths.PAYMENT_CHANGE, PyRequest.POST, dto, self.expectedSuccess, None, "emailToken=" + str(Role.testEmailToken))
        
        if Role.RoleUnlinked in self.overrideRoles[authed]:
            self.overrideRoles[authed].remove(Role.RoleUnlinked)
        
    def testOverrideRoles(self, authed, overrideRoles):
        expected = self.unauthed.getDTOResponse({'overrideRoles':overrideRoles})
        self.unauthed.expectResponse(Paths.USERS_ROLES, PyRequest.GET, None, self.expectedDenied)
        data = authed.expectResponse(Paths.USERS_ROLES, PyRequest.GET, None, expected)
        badRoles = []
        for role in overrideRoles:
            if role not in data['dto']['overrideRoles']:
                badRoles.append(role)
        if len(badRoles) > 0:
            self.error(data['dto']['overrideRoles'], overrideRoles, PyRequest.GET, Paths.USERS_ROLES, None, None)
