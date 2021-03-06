from PyConstants import Paths
from PyConstants import Codes
from PyConstants import CacheTimes
from PyBaseTest import BaseTest
from PyRequest import PyRequest
from Admin import Admin
from random import randrange
import time

class Comment(BaseTest):
    
    def runTests(self, notifications, secondaryToken, secondaryName, postings, lockedUserToken):
        self.notifications = notifications
        self.notifications['comment']['POSTING'] = 0
        self.notifications['comment']['TAG'] = 0
        self.notifications['comment']['USER'] = 0
        self.notifications['comment'][secondaryName] = 0
        self.notifications['comment'][self.username] = 0
        self.notifications['comment'][self.target] = 0
        self.notifications['comment']['backer'] = 0
        self.notifications['comment']['promotion'] = 0
        self.notifications['comment']['backerPromotion'] = 0
        
        self.secondaryAuthed = PyRequest(secondaryToken)
        self.lockedAuthed = PyRequest(lockedUserToken)
        self.secondary = secondaryName
        self.postingsList = postings
        print("Running comment tests")
        expectedFinances = {'code':Codes.SUCCESS}
        expectedCommentsCount = {'code':Codes.SUCCESS}
        
        admin = Admin()
        admin.addCurrency(self.username, 2000)
        admin.addCurrency(self.target, 2000)
        admin.addCurrency(secondaryName, 2000)
        
        #backingBody = {'username':self.username, 'amount':1000}
        #self.targetAuthed.expectResponse(Paths.OFFERS, PyRequest.POST, backingBody, self.expectedSuccess)
        #self.authed.expectResponse(Paths.OFFERS_ACCEPT, PyRequest.POST, None, self.expectedSuccess, self.target)
        self.backer = None
        #self.backer = self.target
        #self.notifications['backing']['offer'] += 1
        #self.notifications['backing']['accept'] += 1
        
        data = self.authed.expectResponse(Paths.FINANCES, PyRequest.GET, None, expectedFinances)
        self.balance = data['dto']['balance']
        data = self.targetAuthed.expectResponse(Paths.FINANCES, PyRequest.GET, None, expectedFinances)
        self.targetBalance = data['dto']['balance']
        
        self.comments = {}
        self.otherCommentsCount = 0
        
        data = self.authed.expectResponse(Paths.COMMENTS, PyRequest.GET, None, expectedCommentsCount, None, ['time=alltime','ctype=posting','ctype=user','ctype=tAg','warning=true'])
        self.otherCommentsCount = data['page']['totalElements']
        
        self.testAddComments('POSTING')
        self.testPromoteComments()
        self.testSort()
        self.testPromoteComments()
        self.testPromoteComments()
        self.testAddComments('TAG')
        self.testSort()
        self.testAddComments('USER')
        self.testAddComments('POSTING')
        
        postingComments = filter(lambda x: self.comments[x]['type'] == 'POSTING', self.comments.keys())
        tagComments = filter(lambda x: self.comments[x]['type'] == 'TAG', self.comments.keys())
        userComments = filter(lambda x: self.comments[x]['type'] == 'USER', self.comments.keys())
                
        parent = tagComments[randrange(len(tagComments))]
        self.testAddComments('TAG', parent)
        self.testSort()
        
        parent = userComments[randrange(len(userComments))]
        self.testAddComments('USER', parent)
        
        parent = postingComments[randrange(len(postingComments))]
        self.testAddComments('POSTING', parent)
        self.testPromoteComments()
        self.testPromoteComments()
        self.testSort()
        self.testComments()
        #self.testTallies()
        #self.testNotifications()
        
        balance = {'balance':self.balance}
        expected = self.unauthed.getDTOResponse(balance)
        self.authed.expectResponse(Paths.FINANCES, PyRequest.GET, None, expected)
        balance = {'balance':self.targetBalance}
        expected = self.unauthed.getDTOResponse(balance)
        self.targetAuthed.expectResponse(Paths.FINANCES, PyRequest.GET, None, expected)
        
        #self.testFlag(self.comments.keys()[0])
        
    def testComments(self):
        time.sleep(CacheTimes.COMMENT)
        commentsCount = 0
        for k in self.comments.keys():
            comment = self.comments[k]
            expected = self.unauthed.getDTOResponse(comment)
            self.unauthed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, expected, k)
            self.authed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, expected, k)
            commentsCount += 1
        
    def testCommentsPaged(self):
        commentsCount = 0
        for k in self.comments.keys():
            comment = self.comments[k]
            expected = self.unauthed.getDTOResponse(comment)
            self.unauthed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, expected, k)
            self.authed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, expected, k)
            commentsCount += 1
        
        page = {'totalElements':self.otherCommentsCount + commentsCount}
        expectedPage = self.unauthed.getPageResponse(page)
        
        self.unauthed.expectResponse(Paths.COMMENTS, PyRequest.GET, None, expectedPage, None, ['time=alltime','ctype=posting','ctype=user','ctype=tAg','warning=true'])
        self.authed.expectResponse(Paths.COMMENTS, PyRequest.GET, None, expectedPage, None, ['time=alltime','ctype=posting','ctype=user','ctype=tAg','warning=true'])
        
        author = {'totalElements':len(self.comments.keys())}
        expectedPage = self.unauthed.getPageResponse(author)
        self.unauthed.expectResponse(Paths.COMMENTS_AUTHOR, PyRequest.GET, None, expectedPage, self.username, ['warning=true'])
        self.authed.expectResponse(Paths.COMMENTS_AUTHOR, PyRequest.GET, None, expectedPage, self.username, ['warning=true'])
        
        self.unauthed.expectResponse(Paths.COMMENTS, PyRequest.GET, None, self.expectedInvalid, None, ['warning=true','user=invalid#%@'])
        self.unauthed.expectResponse(Paths.COMMENTS, PyRequest.GET, None, self.expectedNotFound, None, ['warning=true','user=notFoundName838c'])
        self.unauthed.expectResponse(Paths.COMMENTS, PyRequest.GET, None, expectedPage, None, ['warning=true','user='+self.username])
        
        beneficiary = {'totalElements':len(self.comments.keys()) / 2}
        expectedPage = self.unauthed.getPageResponse(beneficiary)
        #self.unauthed.expectResponse(Paths.COMMENTS_BENEFICIARY, PyRequest.GET, None, expectedPage, self.backer, ['warning=true'])
        #self.authed.expectResponse(Paths.COMMENTS_BENEFICIARY, PyRequest.GET, None, expectedPage, self.backer, ['warning=true'])

            
    def testAddComments(self, type='POSTING', parent=None):
        if parent != None:
            parentAuthor = str(self.comments[parent]['author']['username'])
            submitId = str(self.comments[parent]['base'])
            type = str(self.comments[parent]['type'])
            path = Paths.COMMENTS_COMMENTS
        elif type == 'POSTING':
            path = Paths.POSTINGS_COMMENTS
            keyNum = randrange(len(self.postingsList))
            submitId = self.postingsList[keyNum]
        elif type == 'USER':
            path = Paths.USERS_COMMENTS
            submitId = self.secondary
        else:
            path = Paths.TAGS_COMMENTS
            submitId = 'tag0'
        cost = randrange(1,15)
        content = "This is a test content!"
        
        submission = {'cost':9000,
                      'content':"",
                      'backer':None,
                      'warning':False
                      }
        
        resultSuccess = {'result': self.unauthed.insertExists()}
        createSuccess = self.unauthed.getCustomResponse(Codes.CREATED, resultSuccess, self.unauthed.insertNotExists())
        if parent == None:
            self.authed.expectResponse(path, PyRequest.POST, submission, self.expectedInvalid, submitId)
            submission['content'] = content
            self.unauthed.expectResponse(path, PyRequest.POST, submission, self.expectedDenied, submitId)
            self.authed.expectResponse(path, PyRequest.POST, submission, self.expectedBalance, submitId)
            submission['cost'] = cost
            if type == 'USER':
                self.secondaryAuthed.expectResponse(Paths.BLOCKED_ID, PyRequest.POST, None, self.expectedSuccess, self.username)
                self.authed.expectResponse(path, PyRequest.POST, submission, self.expectedNotAllowed, submitId)
                self.secondaryAuthed.expectResponse(Paths.BLOCKED_ID, PyRequest.DELETE, None, self.expectedSuccess, self.username)
                
                settings = {'options':{'ALLOW_PROFILE_COMMENTS':False}}
                self.secondaryAuthed.expectResponse(Paths.SETTINGS, PyRequest.POST, settings, self.expectedSuccess)
                self.authed.expectResponse(path, PyRequest.POST, submission, self.expectedNotAllowed, submitId)
                settings = {'options':{'ALLOW_PROFILE_COMMENTS':True}}
                self.secondaryAuthed.expectResponse(Paths.SETTINGS, PyRequest.POST, settings, self.expectedSuccess)
            
            if type == 'POSTING':
                # assume it was by same user. possible problem here
                self.authed.expectResponse(Paths.POSTINGS_ID_DISABLE, PyRequest.POST, None, self.expectedSuccess, submitId)
                time.sleep(CacheTimes.POSTING)
                self.secondaryAuthed.expectResponse(path, PyRequest.POST, submission, self.expectedNotAllowed, submitId)
                self.authed.expectResponse(Paths.POSTINGS_ID_ENABLE, PyRequest.POST, None, self.expectedSuccess, submitId)
                time.sleep(CacheTimes.POSTING)
            
            
            data = self.authed.expectResponse(path, PyRequest.POST, submission, createSuccess, submitId)
            self.notifications['comment'][type] += 1
        else:
            self.authed.expectResponse(Paths.COMMENTS_COMMENTS, PyRequest.POST, submission, self.expectedInvalid, parent)
            submission['content'] = content
            self.unauthed.expectResponse(Paths.COMMENTS_COMMENTS, PyRequest.POST, submission, self.expectedDenied, parent)
            self.authed.expectResponse(Paths.COMMENTS_COMMENTS, PyRequest.POST, submission, self.expectedBalance, parent)
            submission['cost'] = cost
            if type == 'USER':
                self.secondaryAuthed.expectResponse(Paths.BLOCKED_ID, PyRequest.POST, None, self.expectedSuccess, self.username)
                self.authed.expectResponse(Paths.COMMENTS_COMMENTS, PyRequest.POST, submission, self.expectedNotAllowed, parent)
                self.secondaryAuthed.expectResponse(Paths.BLOCKED_ID, PyRequest.DELETE, None, self.expectedSuccess, self.username)
                
                settings = {'options':{'ALLOW_PROFILE_COMMENTS':False}}
                self.secondaryAuthed.expectResponse(Paths.SETTINGS, PyRequest.POST, settings, self.expectedSuccess)
                self.authed.expectResponse(Paths.COMMENTS_COMMENTS, PyRequest.POST, submission, self.expectedNotAllowed, parent)
                settings = {'options':{'ALLOW_PROFILE_COMMENTS':True}}
                self.secondaryAuthed.expectResponse(Paths.SETTINGS, PyRequest.POST, settings, self.expectedSuccess)
            
            
            self.authed.expectResponse(Paths.COMMENTS_ID_DISABLE, PyRequest.POST, None, self.expectedSuccess, parent)
            time.sleep(CacheTimes.COMMENT)
            self.secondaryAuthed.expectResponse(Paths.COMMENTS_COMMENTS, PyRequest.POST, submission, self.expectedNotAllowed, parent)
            self.authed.expectResponse(Paths.COMMENTS_ID_ENABLE, PyRequest.POST, None, self.expectedSuccess, parent)
            time.sleep(CacheTimes.COMMENT)
            
            data = self.authed.expectResponse(Paths.COMMENTS_COMMENTS, PyRequest.POST, submission, createSuccess, parent)
            self.notifications['comment'][parentAuthor] += 1

        self.balance -= cost
        id = data['dto']['result']
        
        self.testRemoveComment(id)
        
        tally = {'cost':cost,'promotion':0, 'appreciation':0,'value':cost}
        comment = {'id':id,
                   'base':submitId,
                   'type': type,
                   'author':self.createUsername(self.username),
                   'tally':tally,
                   'content':content,
                   'promotionCount':0,
                   'appreciationCount':0
                   }
        if parent != None:
            comment['parent'] = parent
        self.comments[id] = comment
        
        if self.backer != None and isinstance(self.backer, str):
            backedSubmission = {'cost':cost,
                      'content':content,
                      'backer':self.backer,
                      'warning':False
                      }
            if parent == None:
                data = self.authed.expectResponse(path, PyRequest.POST, backedSubmission, createSuccess, submitId)
                self.notifications['comment'][type] += 1
            else:
                data = self.authed.expectResponse(Paths.COMMENTS_COMMENTS, PyRequest.POST, backedSubmission, createSuccess, parent)
                self.notifications['comment'][parentAuthor] += 1
            backedId = data['dto']['result']
            backedComment = {'id':backedId,
                            'base': submitId,
                            'type': type,
                            'author':self.createUsername(self.username),
                            'tally':tally.copy(),
                            'content':content,
                            'promotionCount':0,
                            'appreciationCount':0,
                            'beneficiary':self.createUsername(self.backer)
                   }
            if parent != None:
                backedComment['parent'] = parent
                
            self.notifications['comment']['backer'] += 1
            self.comments[backedId] = backedComment
        
        #self.testComments()

        edit = ''
        submission = {'content':edit}
        self.authed.expectResponse(Paths.COMMENTS_ID_EDIT, PyRequest.POST, submission, self.expectedInvalid, id)

        time.sleep(CacheTimes.COMMENT)

        edit = 'This is a test edit!'
        submission = {'content':edit}
        self.unauthed.expectResponse(Paths.COMMENTS_ID_EDIT, PyRequest.POST, submission, self.expectedDenied, id) 
        self.secondaryAuthed.expectResponse(Paths.COMMENTS_ID_EDIT, PyRequest.POST, submission, self.expectedNotAllowed, id)
        self.authed.expectResponse(Paths.COMMENTS_ID_EDIT, PyRequest.POST, submission, self.expectedSuccess, id)

        time.sleep(CacheTimes.COMMENT)

        expectedEdit = self.unauthed.getDTOResponse(submission)
        self.unauthed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, expectedEdit, id)
        self.authed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, expectedEdit, id)

        self.comments[id]['content'] = edit
        
    def testPromoteComments(self):
        promotion = randrange(25,55)
        keyNum = randrange(len(self.comments.keys()))
        id = self.comments.keys()[keyNum]
        comment = self.comments[id].copy()
        invalidid = "123"
        submission = {'promotion':9000,'warning':True}
        
        self.unauthed.expectResponse(Paths.COMMENTS_PROMOTE, PyRequest.POST, submission, self.expectedDenied,id)
        self.secondaryAuthed.expectResponse(Paths.COMMENTS_PROMOTE, PyRequest.POST, submission, self.expectedInvalid,invalidid)
        self.secondaryAuthed.expectResponse(Paths.COMMENTS_PROMOTE, PyRequest.POST, submission, self.expectedBalance,id)
        submission = {'promotion':promotion,'warning':True}
        #self.authed.expectResponse(Paths.COMMENTS_PROMOTE, PyRequest.POST, submission, self.expectedNotAllowed,id)
        if 'beneficiary' in comment:
            #self.targetAuthed.expectResponse(Paths.COMMENTS_PROMOTE, PyRequest.POST, submission, self.expectedNotAllowed,id)
            self.notifications['comment']['backerPromotion'] += 1
        self.secondaryAuthed.expectResponse(Paths.COMMENTS_PROMOTE, PyRequest.POST, submission, self.expectedSuccess,id)
            
        self.notifications['comment']['promotion'] += 1
        
        comment['tally']['promotion'] += promotion
        comment['tally']['value'] += promotion
        comment['warning'] = True
        if 'content' in comment:
            del comment['content']
        comment['promotionCount'] += 1
        self.comments[id] = comment
        
    def testRemoveComment(self, cid):
        # testing remove
        expectedNotRemoved = self.unauthed.getDTOResponse({'removed': False})
        expectedRemoved = self.unauthed.getDTOResponse({'removed': True})
        self.authed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, expectedNotRemoved, cid)
        self.authed.expectResponse(Paths.COMMENTS_ID_DISABLE, PyRequest.POST, None, self.expectedSuccess, cid)
        time.sleep(CacheTimes.COMMENT)
        self.authed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, expectedRemoved, cid)
        self.authed.expectResponse(Paths.COMMENTS_ID_ENABLE, PyRequest.POST, None, self.expectedSuccess, cid)
        time.sleep(CacheTimes.COMMENT)
        self.authed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, expectedNotRemoved, cid)
        
        
    def testSort(self):
        time.sleep(CacheTimes.COMMENT)
        expectedPage = self.unauthed.getPageResponse()
        data = self.authed.expectResponse(Paths.COMMENTS, PyRequest.GET, None, expectedPage, None, 
                                          ['size=50', 'page=0', 'sort=value', 'time=alltime','ctype=posting','ctype=user','ctype=tAg'])
        valueList = data['page']['content']
        sortedValueList = sorted(valueList, 
                                 key=lambda x: x['tally']['value'], reverse=True)
        valueList = map(lambda x: {x['id']:x['tally']['value']}, valueList)
        sortedValueList = map(lambda x: {x['id']:x['tally']['value']}, sortedValueList)
        
        data = self.authed.expectResponse(Paths.COMMENTS, PyRequest.GET, None, expectedPage, None, 
                                          ['size=50','page=0', 'sort=value', 'time=hour','ctype=posting','ctype=user','ctype=tAg'])
        hourList = data['page']['content']
        sortedHourList = sorted(hourList, 
                                 key=lambda x: x['tally']['value'], reverse=True)
        hourList = filter(lambda x: x['id'] in self.comments.keys(), hourList)
        sortedHourList = filter(lambda x: x['id'] in self.comments.keys(), sortedHourList)
        hourList = map(lambda x: {x['id']:x['tally']['value']}, hourList)
        sortedHourList = map(lambda x: {x['id']:x['tally']['value']}, sortedHourList)
        
        data = self.authed.expectResponse(Paths.COMMENTS, PyRequest.GET, None, expectedPage, None, 
                                          ['size=50','page=0', 'sort=promotion', 'time=alltime','ctype=posting','ctype=user','ctype=tAg'])
        promotionList = data['page']['content']
        sortedPromotionList = sorted(promotionList, 
                                        key=lambda x: x['tally']['promotion'], reverse=True)
        promotionList = map(lambda x: {x['id']:x['tally']['promotion']}, promotionList)
        sortedPromotionList = map(lambda x: {x['id']:x['tally']['promotion']}, sortedPromotionList)
        
        data = self.authed.expectResponse(Paths.COMMENTS, PyRequest.GET, None, expectedPage, None, 
                                          ['size=50','page=0', 'sort=cost', 'time=alltime','ctype=posting','ctype=user','ctype=tAg'])
        costList = data['page']['content']
        sortedCostList = sorted(costList, key=lambda x: x['tally']['cost'], reverse=True)
        costList = map(lambda x: {x['id']:x['tally']['cost']}, costList)
        sortedCostList = map(lambda x: {x['id']:x['tally']['cost']}, sortedCostList)
        
        valueError = False
        for position, id in enumerate(valueList):
            if id != sortedValueList[position]:
                valueError = True
        hourError = False
        for position, id in enumerate(hourList):
            if id != sortedHourList[position]:
                hourError = True
        
        promotionError = False
        for position, id in enumerate(promotionList):
            if id != sortedPromotionList[position]:
                promotionError = True
        
        costError = False
        for position, id in enumerate(costList):
            if id != sortedCostList[position]:
                costError = True
        
        if valueError:
            self.error(valueList, sortedValueList, PyRequest.GET, Paths.COMMENTS, None, None, ['sort=value','time=alltime','ctype=posting','ctype=user','ctype=tAg'])
        if hourError:
            self.error(hourList, sortedHourList, PyRequest.GET, Paths.COMMENTS, None, None, ['sort=value','time=hour','ctype=posting','ctype=user','ctype=tAg'])
        if promotionError:
            self.error(promotionList, sortedPromotionList, PyRequest.GET, Paths.COMMENTS, None, None, ['sort=promotion','time=alltime','ctype=posting','ctype=user','ctype=tAg'])
        if costError:
            self.error(costList, sortedCostList, PyRequest.GET, Paths.COMMENTS, None, None, ['sort=cost','time=alltime','ctype=posting','ctype=user','ctype=tAg'])
            
    def testNotifications(self):
        page = {'totalElements':self.notifications['comment']['POSTING'] + self.notifications['comment'][self.username]}
        expected = self.unauthed.getPageResponse(page)
        self.authed.expectResponse(Paths.NOTIFICATIONS, PyRequest.GET, None, expected, None, ['event=comment','event=comment_sub'])
        
        page = {'totalElements':self.notifications['comment']['USER'] + self.notifications['comment'][self.secondary]}
        expected = self.unauthed.getPageResponse(page)
        self.secondaryAuthed.expectResponse(Paths.NOTIFICATIONS, PyRequest.GET, None, expected, None, ['event=comment','event=comment_sub'])
        
        page = {'totalElements':self.notifications['comment']['promotion']}
        expected = self.unauthed.getPageResponse(page)
        self.authed.expectResponse(Paths.NOTIFICATIONS, PyRequest.GET, None, expected, None, 'event=promotion_comment')
        
        page = {'totalElements':self.notifications['comment']['backer'] + self.notifications['comment'][self.target]}
        expected = self.unauthed.getPageResponse(page)
        self.targetAuthed.expectResponse(Paths.NOTIFICATIONS, PyRequest.GET, None, expected, None, ['event=comment','event=comment_sub'])
        
        page = {'totalElements':self.notifications['comment']['backerPromotion']}
        expected = self.unauthed.getPageResponse(page)
        self.targetAuthed.expectResponse(Paths.NOTIFICATIONS, PyRequest.GET, None, expected, None, 'event=promotion_comment')
        
    def testFlag(self, id):
        data = self.lockedAuthed.expectResponse(Paths.USERS_CURRENT, PyRequest.GET, None, self.unauthed.getDTOResponse())
        admin = Admin()
        admin.addCurrency(data['dto']['username']['username'], 2000)

        path = Paths.POSTINGS_COMMENTS
        keyNum = randrange(len(self.postingsList))
        submitId = self.postingsList[keyNum]
        
        cost = 2
        
        content = 'Flagged content'
        submission = {'cost':cost,
                      'content':content,
                      'backer':None,
                      'warning':False
                      }
        
        data = self.lockedAuthed.expectResponse(Paths.POSTINGS_COMMENTS, PyRequest.POST, submission, self.expectedResultCreated, submitId)
        
        id = data['dto']['result']
        
        tally = {'cost':cost,'promotion':0, 'appreciation':0,'value':cost}
        comment = {'id':id,
                   'base':submitId,
                   'type': type,
                   'tally':tally,
                   'content':content,
                   'promotionCount':0,
                   'appreciationCount':0,
                   'removed':False
                   }
        
        time.sleep(CacheTimes.COMMENT)
        self.unauthed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, self.unauthed.getDTOResponse(comment), id)
        comment['removed'] = True
        
        self.authed.expectResponse(Paths.COMMENTS_ID_FLAG, PyRequest.POST, None, self.expectedSuccess, id)
        self.targetAuthed.expectResponse(Paths.COMMENTS_ID_FLAG, PyRequest.POST, None, self.expectedSuccess, id)
        self.secondaryAuthed.expectResponse(Paths.COMMENTS_ID_FLAG, PyRequest.POST, None, self.expectedSuccess, id)
        
        #self.unauthed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, self.unauthed.getDTOResponse(comment), id)
        #self.lockedAuthed.expectResponse(Paths.USERS_CURRENT, PyRequest.GET, None, self.expectedLocked)
        
    def testTallies(self):
        #with both cacheing and aggregation, may not be able to get an accurate count on this due to differences between fetching the base, and then comparing
        time.sleep(CacheTimes.COMMENT + CacheTimes.POSTING + CacheTimes.TAG)
        postings = {}
        users = {}
        tags = {}
        for c in self.comments.keys():
            v = self.comments[c]
            id = v['base']
            type = v['type']
            if type == 'POSTING':
                if id not in postings:
                    postings[id] = {'value':0, 'cost':0, 'promotion':0, 'appreciation':0}
            elif type == 'USER':
                if id not in users:
                    users[id] = {'value':0, 'cost':0, 'promotion':0, 'appreciation':0}
            elif type == 'TAG':
                if id not in tags:
                    tags[id] = {'value':0, 'cost':0, 'promotion':0, 'appreciation':0}
                
        for pid in postings:
            data = self.authed.expectResponse(Paths.POSTINGS_COMMENTS, PyRequest.GET, None, self.unauthed.getPageResponse(), pid, ['size=50','time=alltime','ctype=posting','ctype=user','ctype=tAg','warning=true'])
            comments = data['page']['content']
            for c in comments:
                rc = self.testCommentTallies(c['id'])
                postings[pid]['value'] += rc['value']
                postings[pid]['cost'] += rc['cost']
                postings[pid]['promotion'] += rc['promotion']
            
            expected = self.unauthed.getDTOResponse({'replyTally':postings[pid]})
            self.authed.expectResponse(Paths.POSTINGS_ID, PyRequest.GET, None, expected, pid)
            
        for uid in users:
            data = self.authed.expectResponse(Paths.USERS_COMMENTS, PyRequest.GET, None, self.unauthed.getPageResponse(), uid, ['size=50','time=alltime','ctype=posting','ctype=user','ctype=tAg','warning=true'])
            comments = data['page']['content']
            for c in comments:
                rc = self.testCommentTallies(c['id'])
                users[uid]['value'] += rc['value']
                users[uid]['cost'] += rc['cost']
                users[uid]['promotion'] += rc['promotion']
            
            expected = self.unauthed.getDTOResponse({'replyTally':users[uid]})
            self.authed.expectResponse(Paths.USERS_ID, PyRequest.GET, None, expected, uid)
            
        for tag in tags:
            data = self.authed.expectResponse(Paths.TAGS_COMMENTS, PyRequest.GET, None, self.unauthed.getPageResponse(), tag, ['size=50','time=alltime','ctype=posting','ctype=user','ctype=tAg','warning=true'])
            comments = data['page']['content']
            for c in comments:
                rc = self.testCommentTallies(c['id'])
                tags[tag]['value'] += rc['value']
                tags[tag]['cost'] += rc['cost']
                tags[tag]['promotion'] += rc['promotion']
            
            expected = self.unauthed.getDTOResponse({'replyTally':tags[tag]})
            self.authed.expectResponse(Paths.TAGS_ID, PyRequest.GET, None, expected, tag)

            
            
    def testCommentTallies(self, cid):
        data = self.authed.expectResponse(Paths.COMMENTS_COMMENTS, PyRequest.GET, None, self.unauthed.getPageResponse(), cid,  ['size=50','time=alltime','ctype=posting','ctype=user','ctype=tAg','warning=true'])
        comments = data['page']['content']
        comment = {'value':0, 'cost':0, 'promotion':0, 'appreciation':0}
        #fullComment = {'value':0, 'cost':0, 'promotion':0, 'appreciation':'0'}
        for c in comments:
            fc = self.testCommentTallies(c['id'])
            comment['value'] += c['tally']['value']
            comment['cost'] += c['tally']['cost']
            comment['promotion'] += c['tally']['promotion']
            #only 1 depth of adding rather than summing all subcomments
            #fullComment['value'] += c['tally']['value'] + fc['value']
            #fullComment['cost'] += c['tally']['cost'] + fc['cost']
            #fullComment['promotion'] += c['tally']['promotion'] + fc['promotion']
        
        expected = self.unauthed.getDTOResponse({'replyTally':comment})
        data = self.authed.expectResponse(Paths.COMMENTS_ID, PyRequest.GET, None, expected, cid)
        replyTally = data['dto']['tally']

        return replyTally
        
