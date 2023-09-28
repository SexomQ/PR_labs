from player import Player
import json
import datetime
import xmltodict
import dicttoxml
import xml.etree.ElementTree as ET
import player_pb2 as pb
from google.protobuf.json_format import MessageToDict, Parse


class PlayerFactory:
    def to_json(self, players):
        '''
            This function should transform a list of Player objects into a list with dictionaries.
        '''
        list_of_dict = []

        for player in players:
            pl_nick = player.nickname
            pl_email = player.email
            pl_dob = str(player.date_of_birth)[:10]
            pl_xp = player.xp
            pl_cls = player.cls

            pl_dict = {
                "nickname":pl_nick,
                "email":pl_email,
                "date_of_birth":pl_dob,
                "xp":pl_xp,
                "class":pl_cls
            }
            list_of_dict.append(pl_dict)

        return list_of_dict

    def from_json(self, list_of_dict):
        '''
            This function should transform a list of dictionaries into a list with Player objects.
        '''

        players = []
        for dict in list_of_dict:
            players.append(Player(nickname=dict["nickname"], email=dict["email"], date_of_birth=dict["date_of_birth"], xp=dict["xp"], cls=dict["class"]))


        return players

    def from_xml(self, xml_string):
        '''
            This function should transform a XML string into a list with Player objects.
        '''
        players = []
        root = ET.fromstring(xml_string)
        for player in root.iter("player"):
            player_class = Player(
                nickname = player.find('nickname').text,
                email = player.find('email').text,
                date_of_birth = player.find('date_of_birth').text,
                xp = int(player.find('xp').text),
                cls = player.find('class').text
            )

            players.append(player_class)
        
        return players


    def to_xml(self, list_of_players):
        '''
            This function should transform a list with Player objects into a XML string.
        '''
        root = ET.Element("data")
        for player in list_of_players:
            player_elem = ET.Element("player")
            nickname_elem = ET.Element("nickname")
            nickname_elem.text = player.nickname
            email_elem = ET.Element("email")
            email_elem.text = player.email
            dob_elem = ET.Element("date_of_birth")
            dob_elem.text = player.date_of_birth.strftime("%Y-%m-%d")
            xp_elem = ET.Element("xp")
            xp_elem.text = str(player.xp)
            class_elem = ET.Element("class")
            class_elem.text = player.cls
            player_elem.extend([nickname_elem, email_elem, dob_elem, xp_elem, class_elem])
            root.append(player_elem)
        return ET.tostring(root, encoding="utf-8").decode("utf-8")
    
    def from_protobuf(self, binary):
        '''
            This function should transform a binary protobuf string into a list with Player objects.
        '''
        request = pb.PlayersList()
        request.ParseFromString(binary)
        dict_protobuf = MessageToDict(request)
        players = []
        for player in dict_protobuf['player']:
            players.append(Player(
                player['nickname'], 
                player['email'], 
                player['dateOfBirth'], 
                player['xp'], 
                player['cls']))

        return players

    def to_protobuf(self, list_of_players):
        '''
            This function should transform a list with Player objects into a binary protobuf string.
        '''
        blueprint = pb.PlayersList()
        list_dict_player = []
        for player in list_of_players:
            # crete a dict with the player data
            player = {
                'nickname': player.nickname,
                'email': player.email,
                'dateOfBirth': player.date_of_birth.strftime("%Y-%m-%d"),
                'xp': player.xp,
                'cls': player.cls
            }
            # append the dict to the list
            list_dict_player.append(player)
        final_dict = {'player': list_dict_player}
        json_string = json.dumps(final_dict)
        Parse(str(json_string), blueprint)
        return blueprint.SerializeToString()

