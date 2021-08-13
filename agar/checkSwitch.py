class Switch:
    switch = 1

    @staticmethod
    def get_switch():
        if Switch.switch == 1:
            Switch.switch = -1
            return Switch.switch
        else:
            Switch.switch = 1
            return Switch.switch


    