from __future__ import annotations
from bson import ObjectId

from bpr_data.repository import Repository, Collection
from bpr_data.models.invitation import Invitation, InvitationGetModel

import src.services.workspace_service as workspace_service
import src.services.users_service as users_service
import settings

db = Repository.get_instance(**settings.MONGO_CONN)

collection = Collection.INVITATION


def add_invitation(invitation: Invitation) -> Invitation:
    insert_result = db.insert(collection, invitation)
    if insert_result is not None:
        return Invitation.from_dict(insert_result)


def get_invitation_by_id(invitation_id: str) -> Invitation:
    result = db.find_one(collection, id=invitation_id)
    if result is not None:
        return Invitation.from_dict(result)


def delete_invitation(invitation_id: str) -> bool:
    return db.delete(collection, id=invitation_id)


def get_invitation(workspace_id: ObjectId, invitee_email_address: str) -> Invitation:
    invitation = db.find_one(collection=collection,
                             workspaceId=workspace_id,
                             inviteeEmailAddress=invitee_email_address)
    if invitation is not None:
        return Invitation.from_dict(invitation)


def get_workspace_invitations_for_user(email: str) -> list:
    find_result = db.find(collection=collection, inviteeEmailAddress=email)
    if find_result is not None:
        invitations = Invitation.from_dict_list(find_result)
        invitation_get_models = []
        for invitation in invitations:
            invitation_get_models.append(get_invitation_get_model(invitation))
        return invitation_get_models


def get_invitation_get_model(invitation: Invitation):
    workspace = workspace_service.get_workspace(invitation.workspaceId)
    user = users_service.get_user(invitation.inviterId)
    return InvitationGetModel(
        _id=invitation._id,
        inviterId=invitation.inviterId,
        workspaceId=invitation.workspaceId,
        inviteeEmailAddress=invitation.inviteeEmailAddress,
        workspaceName=workspace.name,
        inviterUserName=user.name
    )
