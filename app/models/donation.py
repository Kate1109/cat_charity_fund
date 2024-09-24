from sqlalchemy import Column, Integer, ForeignKey, Text

from app.models.base import CharityProjectDonationBase


class Donation(CharityProjectDonationBase):
    user_id = Column(Integer, ForeignKey(
        'user.id', name='fk_user_id'
    ))
    comment = Column(Text)
