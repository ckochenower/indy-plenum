import pytest
from zeno.common.request_types import InstanceChange
from zeno.server.node import Node
from zeno.test.eventually import eventually

from zeno.common.exceptions import SuspiciousNode
from zeno.server.suspicion_codes import Suspicions
from zeno.test.helper import getAllArgs, getNodeSuspicions

nodeCount = 7

@pytest.mark.xfail(reason="Not yet implemented")
def testDuplicateInstanceChangeMsgsMarkNodeAsSuspicious(looper, nodeSet, up):
    maliciousNode = nodeSet.Alpha
    maliciousNode.send(InstanceChange(0))

    def chk(instId):
        for node in nodeSet:
            if node.name != maliciousNode.name:
                param = getAllArgs(node, Node.processInstanceChange)
                assert param[0]['instChg'].viewNo == instId
                assert param[0]['frm'] == maliciousNode.name

    looper.run(eventually(chk, 0, retryWait=1, timeout=20))
    maliciousNode.send(InstanceChange(0))

    def g():
        for node in nodeSet:
            if node.name != maliciousNode.name:
                frm, reason, code = getAllArgs(node, Node.reportSuspiciousNode)
                assert frm == maliciousNode.name
                assert isinstance(reason, SuspiciousNode)
                assert len(getNodeSuspicions(node,
                                             Suspicions.DUPLICATE_INST_CHNG.code)) == 12

    looper.run(eventually(g, retryWait=1, timeout=20))


@pytest.mark.xfail(reason="Not yet implemented")
def testMultipleInstanceChangeMsgsMarkNodeAsSuspicious(looper, nodeSet, up):
    maliciousNode = nodeSet.Alpha
    for i in range(0, 5):
        maliciousNode.send(InstanceChange(i))

    def chk(instId):
        for node in nodeSet:
            if node.name != maliciousNode.name:
                args = getAllArgs(node, Node.processInstanceChange)
                assert len(args) == 5
                for arg in args:
                    assert arg['frm'] == maliciousNode.name

    for i in range(0, 5):
        looper.run(eventually(chk, i, retryWait=1, timeout=20))

    def g():
        for node in nodeSet:
            if node.name != maliciousNode.name:
                frm, reason, code = getAllArgs(node, Node.reportSuspiciousNode)
                assert frm == maliciousNode.name
                assert isinstance(reason, SuspiciousNode)
                assert len(getNodeSuspicions(node,
                                             Suspicions.FREQUENT_INST_CHNG.code)) == 13

    looper.run(eventually(g, retryWait=1, timeout=20))
