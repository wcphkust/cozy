import unittest

from cozy.rep_inference import infer_rep, pprint_rep, pprint_reps
from cozy.syntax_tools import mk_lambda, pprint, free_vars, all_exps
from cozy.target_syntax import *
from cozy.typecheck import typecheck, retypecheck

class TestRepInference(unittest.TestCase):

    def test_the_filter_typing(self):
        x = EVar("x").with_type(TBag(TInt()))
        y = EVar("y").with_type(TInt())
        e = EUnaryOp("the", EFilter(x, mk_lambda(x.type.t, lambda elem: EBinOp(elem, "==", y).with_type(TBool()))).with_type(x.type)).with_type(TMaybe(x.type.t))
        for (vars, e2) in infer_rep([x], e):
            for (v, proj) in vars:
                errs = typecheck(proj, env={ "x": x.type })
                assert not errs, "whoops! type error: {}".format(errs)
            errs = typecheck(e2, env=dict([(v.id, proj.type) for (v, proj) in vars] + [(x.id, x.type), (y.id, y.type)]))
            assert not errs, "whoops! type error: {}\nstate: {}\nres: {}".format(errs, vars, e2)

    def test_the_map_typing(self):
        x = EVar("x").with_type(TBag(TInt()))
        y = EVar("y").with_type(TInt())
        e = EUnaryOp("the", EMap(x, mk_lambda(x.type.t, lambda elem: EBinOp(elem, "==", y).with_type(TBool()))).with_type(x.type)).with_type(TMaybe(x.type.t))
        for (vars, e2) in infer_rep([x], e):
            for (v, proj) in vars:
                errs = typecheck(proj, env={ "x": x.type })
                assert not errs, "whoops! type error: {}".format(errs)
            errs = typecheck(e2, env=dict([(v.id, proj.type) for (v, proj) in vars] + [(x.id, x.type), (y.id, y.type)]))
            assert not errs, "whoops! type error: {}\nstate: {}\nres: {}".format(errs, vars, e2)

    def test_binop_typechecking(self):
        ys = EVar('ys').with_type(TBag(THandle('ys', TInt())))
        e = EBinOp(EBool(True).with_type(TBool()), 'and', EBinOp(ENum(0).with_type(TInt()), 'in', EMap(ys, ELambda(EVar('y').with_type(THandle('ys', TInt())), EGetField(EVar('y').with_type(THandle('ys', TInt())), 'val').with_type(TInt()))).with_type(TBag(TInt()))).with_type(TBool())).with_type(TBool())
        infer_rep([ys], e, validate_types=True)

    def test_binop(self):
        state = [EVar('xs').with_type(TBag(THandle('xs', TInt()))), EVar('ys').with_type(TBag(THandle('ys', TInt())))]
        e = EBinOp(EVar('ys').with_type(TBag(THandle('ys', TInt()))), '==', EEmptyList().with_type(TBag(THandle('ys', TInt())))).with_type(TBool())
        assert retypecheck(e)
        infer_rep(state, e, validate_types=True)

    def test_filter(self):
        state = [EVar('xs').with_type(TBag(THandle('xs', TInt()))), EVar('ys').with_type(TBag(THandle('ys', TInt())))]
        e = EFilter(EEmptyList().with_type(TBag(THandle('xs', TInt()))), ELambda(EVar('_var15').with_type(THandle('xs', TInt())), EBinOp(EVar('ys').with_type(TBag(THandle('ys', TInt()))), '==', EEmptyList().with_type(TBag(THandle('ys', TInt())))).with_type(TBool()))).with_type(TBag(THandle('xs', TInt())))
        assert retypecheck(e)
        infer_rep(state, e, validate_types=True)

    def test_map(self):
        state = [EVar('xs').with_type(TBag(THandle('xs', TInt()))), EVar('ys').with_type(TBag(THandle('ys', TInt())))]
        e = EMap(EEmptyList().with_type(TBag(THandle('xs', TInt()))), ELambda(EVar('_var15').with_type(THandle('xs', TInt())), EBinOp(EVar('ys').with_type(TBag(THandle('ys', TInt()))), '==', EEmptyList().with_type(TBag(THandle('ys', TInt())))).with_type(TBool()))).with_type(TBag(TBool()))
        assert retypecheck(e)
        infer_rep(state, e, validate_types=True)

    def test_regression1(self):
        state = [EVar('xs').with_type(TBag(THandle('xs', TInt()))), EVar('ys').with_type(TBag(THandle('ys', TInt())))]
        e = EFilter(EMap(EVar('ys').with_type(TBag(THandle('ys', TInt()))), ELambda(EVar('y').with_type(THandle('ys', TInt())), EGetField(EVar('y').with_type(THandle('ys', TInt())), 'val').with_type(TInt()))).with_type(TBag(TInt())), ELambda(EVar('_var11').with_type(TInt()), EBinOp(EVar('_var11').with_type(TInt()), '==', EUnaryOp('sum', EMap(EFilter(EMap(EVar('ys').with_type(TBag(THandle('ys', TInt()))), ELambda(EVar('y').with_type(THandle('ys', TInt())), EGetField(EVar('y').with_type(THandle('ys', TInt())), 'val').with_type(TInt()))).with_type(TBag(TInt())), ELambda(EVar('_var11').with_type(TInt()), EBinOp(EVar('_var11').with_type(TInt()), '==', ENum(0).with_type(TInt())).with_type(TBool()))).with_type(TBag(TInt())), ELambda(EVar('_var12').with_type(TInt()), ENum(1).with_type(TInt()))).with_type(TBag(TInt()))).with_type(TInt())).with_type(TBool()))).with_type(TBag(TInt()))
        assert retypecheck(e)
        infer_rep(state, e, validate_types=True)

    def test_map_get(self):
        state = [EVar('xs').with_type(TBag(THandle('xs', TInt()))), EVar('ys').with_type(TBag(THandle('ys', TInt())))]
        e = EFilter(EMap(EVar('ys').with_type(TBag(THandle('ys', TInt()))), ELambda(EVar('y').with_type(THandle('ys', TInt())), EGetField(EVar('y').with_type(THandle('ys', TInt())), 'val').with_type(TInt()))).with_type(TBag(TInt())), ELambda(EVar('_var11').with_type(TInt()), EBinOp(EVar('_var11').with_type(TInt()), '==', EUnaryOp('sum', EMap(EMapGet(EMakeMap(EVar('ys').with_type(TBag(THandle('ys', TInt()))), ELambda(EVar('_var31').with_type(THandle('ys', TInt())), EVar('_var31').with_type(THandle('ys', TInt()))), ELambda(EVar('_var34').with_type(TBag(THandle('ys', TInt()))), EVar('_var34').with_type(TBag(THandle('ys', TInt()))))).with_type(TMap(THandle('ys', TInt()), TBag(THandle('ys', TInt())))), EVar('_var16').with_type(THandle('ys', TInt()))).with_type(TBag(THandle('ys', TInt()))), ELambda(EVar('_var32').with_type(THandle('ys', TInt())), EGetField(EVar('_var32').with_type(THandle('ys', TInt())), 'val').with_type(TInt()))).with_type(TBag(TInt()))).with_type(TInt())).with_type(TBool()))).with_type(TBag(TInt()))
        assert retypecheck(e)
        infer_rep(state, e, validate_types=True)

    def test_regression2(self):
        state = [EVar('employees').with_type(TBag(THandle('employees', TRecord((('employee_name', TNative('EmployeeName')), ('employer_id', TNative('EmployerId'))))))), EVar('employers').with_type(TBag(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId')))))))]
        e = EFilter(EEmptyList().with_type(TBag(THandle('employees', TRecord((('employee_name', TNative('EmployeeName')), ('employer_id', TNative('EmployerId'))))))), ELambda(EVar('_var11').with_type(THandle('employees', TRecord((('employee_name', TNative('EmployeeName')), ('employer_id', TNative('EmployerId')))))), EUnaryOp('not', EBinOp(EEmptyList().with_type(TBag(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId'))))))), '==', EMapGet(EMakeMap(EVar('employers').with_type(TBag(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId'))))))), ELambda(EVar('_var48').with_type(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId')))))), EVar('_var48').with_type(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId'))))))), ELambda(EVar('_var53').with_type(TBag(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId'))))))), EVar('_var53').with_type(TBag(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId'))))))))).with_type(TMap(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId'))))), TBag(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId')))))))), EVar('_var12').with_type(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId'))))))).with_type(TBag(THandle('employers', TRecord((('employer_name', TNative('EmployerName')), ('employer_id', TNative('EmployerId')))))))).with_type(TBool())).with_type(TBool()))).with_type(TBag(THandle('employees', TRecord((('employee_name', TNative('EmployeeName')), ('employer_id', TNative('EmployerId')))))))
        assert retypecheck(e)
        infer_rep(state, e, validate_types=True)

    def test_regression3(self):
        state = [EVar('users').with_type(TBag(THandle('User', TRecord((('username', TString()), ('salt', TString()), ('storedKey', TString()), ('serverKey', TString()), ('iterations', TInt()), ('name', TString()), ('email', TString()), ('creationDate', TNative('java.util.Date')), ('modificationDate', TNative('java.util.Date'))))))), EVar('rosterItems').with_type(TBag(THandle('RosterItem', TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType'))))))), EVar('groups').with_type(TBag(THandle('Group', TRecord((('name', TString()), ('description', TString()), ('rosterMode', TEnum(('NOBODY', 'ONLY_GROUP', 'EVERYBODY')))))))), EVar('childGroups').with_type(TBag(THandle('_HandleType156', TTuple((THandle('Group', TRecord((('name', TString()), ('description', TString()), ('rosterMode', TEnum(('NOBODY', 'ONLY_GROUP', 'EVERYBODY')))))), THandle('Group', TRecord((('name', TString()), ('description', TString()), ('rosterMode', TEnum(('NOBODY', 'ONLY_GROUP', 'EVERYBODY'))))))))))), EVar('groupMembers').with_type(TBag(THandle('_HandleType159', TTuple((THandle('Group', TRecord((('name', TString()), ('description', TString()), ('rosterMode', TEnum(('NOBODY', 'ONLY_GROUP', 'EVERYBODY')))))), THandle('User', TRecord((('username', TString()), ('salt', TString()), ('storedKey', TString()), ('serverKey', TString()), ('iterations', TInt()), ('name', TString()), ('email', TString()), ('creationDate', TNative('java.util.Date')), ('modificationDate', TNative('java.util.Date')))))))))), EVar('admins').with_type(TBag(THandle('_HandleType162', TTuple((THandle('Group', TRecord((('name', TString()), ('description', TString()), ('rosterMode', TEnum(('NOBODY', 'ONLY_GROUP', 'EVERYBODY')))))), THandle('User', TRecord((('username', TString()), ('salt', TString()), ('storedKey', TString()), ('serverKey', TString()), ('iterations', TInt()), ('name', TString()), ('email', TString()), ('creationDate', TNative('java.util.Date')), ('modificationDate', TNative('java.util.Date'))))))))))]
        e = EUnaryOp('sum', ESingleton(EUnaryOp('sum', EMap(EFilter(EFilter(EVar('rosterItems').with_type(TBag(THandle('RosterItem', TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType'))))))), ELambda(EVar('_var241').with_type(THandle('RosterItem', TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType')))))), EBinOp(ECall('toBareJid', (EGetField(EGetField(EVar('_var241').with_type(THandle('RosterItem', TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType')))))), 'val').with_type(TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType'))))), 'target').with_type(TNative('org.xmpp.packet.JID')),)).with_type(TString()), '==', EGetField(EGetField(EVar('target').with_type(THandle('User', TRecord((('username', TString()), ('salt', TString()), ('storedKey', TString()), ('serverKey', TString()), ('iterations', TInt()), ('name', TString()), ('email', TString()), ('creationDate', TNative('java.util.Date')), ('modificationDate', TNative('java.util.Date')))))), 'val').with_type(TRecord((('username', TString()), ('salt', TString()), ('storedKey', TString()), ('serverKey', TString()), ('iterations', TInt()), ('name', TString()), ('email', TString()), ('creationDate', TNative('java.util.Date')), ('modificationDate', TNative('java.util.Date'))))), 'username').with_type(TString())).with_type(TBool()))).with_type(TBag(THandle('RosterItem', TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType'))))))), ELambda(EVar('_var241').with_type(THandle('RosterItem', TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType')))))), EBinOp(EGetField(EGetField(EVar('_var240').with_type(THandle('User', TRecord((('username', TString()), ('salt', TString()), ('storedKey', TString()), ('serverKey', TString()), ('iterations', TInt()), ('name', TString()), ('email', TString()), ('creationDate', TNative('java.util.Date')), ('modificationDate', TNative('java.util.Date')))))), 'val').with_type(TRecord((('username', TString()), ('salt', TString()), ('storedKey', TString()), ('serverKey', TString()), ('iterations', TInt()), ('name', TString()), ('email', TString()), ('creationDate', TNative('java.util.Date')), ('modificationDate', TNative('java.util.Date'))))), 'username').with_type(TString()), '==', EGetField(EGetField(EVar('_var241').with_type(THandle('RosterItem', TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType')))))), 'val').with_type(TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType'))))), 'user').with_type(TString())).with_type(TBool()))).with_type(TBag(THandle('RosterItem', TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType'))))))), ELambda(EVar('_var241').with_type(THandle('RosterItem', TRecord((('backendId', TLong()), ('user', TString()), ('target', TNative('org.xmpp.packet.JID')), ('nickname', TString()), ('askStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.AskType')), ('recvStatus', TNative('org.jivesoftware.openfire.roster.RosterItem.RecvType')))))), ENum(1).with_type(TInt()))).with_type(TBag(TInt()))).with_type(TInt())).with_type(TBag(TInt()))).with_type(TInt())
        for (st, ee) in infer_rep(state, e, validate_types=False):
            # expression uses 'rosterItems', so we need some inferred state
            assert len(st) > 0, pprint_rep((st, ee))

    def test_nested_makemap(self):
        state = EVar("st").with_type(TBag(TTuple((TInt(), TInt()))))
        x = EVar("x").with_type(state.type.t.ts[0])
        y = EVar("y").with_type(state.type.t.ts[1])
        e1 = EMapGet(EMakeMap(state, mk_lambda(state.type.t, lambda k: ETupleGet(k, 0)), mk_lambda(state.type, lambda vs: vs)), x)
        e2 = EMapGet(EMakeMap(e1,    mk_lambda(state.type.t, lambda k: ETupleGet(k, 1)), mk_lambda(state.type, lambda vs: vs)), y)
        retypecheck(e2)
        reps = list(infer_rep([state], e2, validate_types=True))
        assert reps
        pprint_reps(reps)
        for (st, ee) in reps:
            for e in all_exps(ee):
                assert not isinstance(e, EMakeMap)

    def test_regression4(self):
        pprint_reps(infer_rep(
            [EVar('ints').with_type(TBag(THandle('_HandleType12', TInt())))],
            EUnaryOp('not', EBinOp(ENum(0).with_type(TInt()), '==', EUnaryOp('sum', EMapGet(EVar('_var1141').with_type(TMap(TInt(), TBag(TInt()))), EVar('i').with_type(TInt())).with_type(TBag(TInt()))).with_type(TInt())).with_type(TBool())).with_type(TBool()),
            validate_types=True))
