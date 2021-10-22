class Invitation:
    def __init__(self, inviter_id, workspace_id, invitee_email_address, id=None):
        self.inviter_id = inviter_id
        self.workspace_id = workspace_id
        self.invitee_email_address = invitee_email_address
        if id != None:
            self._id = id

    def from_dict(the_dict: dict):
        inviter_id = the_dict["inviter_id"]
        workspace_id = the_dict["workspace_id"]
        invitee_email_address = the_dict["invitee_email_address"]
        _id = the_dict["_id"]
        return Invitation(inviter_id, workspace_id, invitee_email_address, _id)

