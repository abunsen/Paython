from nose.tools import assert_equals, with_setup

def setup():
    """setting up the test"""
    # TODO here we add the useful global vars
    global global_var
    global_var = "is this a global?"

def teardown():
    """teardowning the test"""
    # TODO add something to do when exiting
    pass

@with_setup(setup, teardown)
def test():
    """testing Authorize.Net"""
    # TODO write the actual test
    #assert_equals(False, "we're fucked, but the global var we set == {0}".format(global_var))
    pass
