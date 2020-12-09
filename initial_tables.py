from app import models
from app.base import Session, engine, Base


Base.metadata.create_all(engine)
session = Session()

class User():
    def user_ins(self):
        newUser = models.User(username = 'testuser',
                            email = 'testuser@adelphi.edu',
                            password = 'secret',
                            fname = 'Test',
                            lname = 'User',
                            userType = 'user',
                            #incidents is a relationship not a column
                            #incidents = ''
                            incident_assigned = None
                            )
        session.add(newUser)
        session.commit()

class Incident():
    def incident_ins(self):
        newIncident = models.Incident(category='medium',
                title = 'testTitle',
                description = 'test description',
                date_created = '2020-12-01',
                date_resolved=None,
                state = 'open',
                tag = 123,
                case_history = 'created today',
                point_of_contact = 1        
                            
                )
        session.add(newIncident)
        session.commit()


if __name__ == '__main__':
    initial = User()
    initial.user_ins()
    incident = Incident()
    incident.incident_ins()





