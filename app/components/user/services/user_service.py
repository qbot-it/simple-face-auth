import numpy as np
from sqlalchemy.exc import IntegrityError
from app.db.database import Session
from ..dto.descriptor import Descriptor
from ..exceptions.user_already_exists import UserAlreadyExistsException
from ..exceptions.user_not_found import UserNotFoundException
from ...user.models.user import User


class UserService:

    def get_one(self, email: str) -> User | None:
        """
         :raises UserNotFoundException
         """

        with Session() as session:
            user = session.query(User).where(User.email == email).first()

            if not isinstance(user, User):
                raise UserNotFoundException()

            return user

    def create(self, email: str, descriptor: Descriptor) -> User | None:
        """
         :raises UserAlreadyExistsException
         """
        with Session() as session:
            user = session.query(User).where(User.email == email).first()

            if isinstance(user, User):
                raise UserAlreadyExistsException()

            try:
                user = User()
                user.email = email
                user.descriptor = descriptor.to_json()
                session.add(user)
                session.commit()
                session.refresh(user)

                return user
            except IntegrityError:
                session.rollback()
                return None

    def update(self, email: str, descriptor: Descriptor) -> User | None:
        """
         :raises UserNotFoundException
         """

        with Session() as session:
            user = session.query(User).where(User.email == email).first()

            if not isinstance(user, User):
                raise UserNotFoundException()

            old_descriptor = Descriptor.from_json(user.descriptor)
            old_descriptor.lbph = np.concatenate((old_descriptor.lbph, descriptor.lbph), axis=0)
            user.descriptor = old_descriptor.to_json()

            try:
                session.commit()
                session.refresh(user)

                return user
            except IntegrityError:
                session.rollback()
                return None

    def delete_all(self):
        with Session() as session:
            session.query(User).delete()
            session.commit()
