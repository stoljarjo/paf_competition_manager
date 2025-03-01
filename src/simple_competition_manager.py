#! /usr/bin/env python3

from dataclasses import dataclass

import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point


def get_distance(p_1: Point, p_2_: Point):
    """
    return distance of two points
    """
    return ((p_1.x - p_2_.x) ** 2 + (p_1.y - p_2_.y) ** 2 + (p_1.z - p_2_.z) ** 2) ** 0.5


@dataclass
class CompetitionManagerNode:
    start_position: Point = None
    goal_position: Point = None
    start_time: float = None
    end_time: float = None
    started: bool = False
    finished: bool = False

    def __post_init__(self):
        while self.goal_position is None or self.start_position is None:
            try:
                self.goal_position = Point(
                    x=rospy.get_param('competition/goal/position/x'),
                    y=rospy.get_param('competition/goal/position/y'),
                    z=rospy.get_param('competition/goal/position/z'))

                self.start_position = Point(
                    x=rospy.get_param('competition/start/position/x'),
                    y=rospy.get_param('competition/start/position/y'),
                    z=rospy.get_param('competition/start/position/z'))
            except rospy.ServiceException as service_error:
                print(f'Ros param not ready! Error: {service_error}')
        print(f'Start {self.start_position}; End {self.goal_position}')

    def callback(self, data: Odometry):
        rospy.logdebug(data)
        current_position = data.pose.pose.position
        print(f'Current_pos_competition: {current_position}')
        distance_to_goal = get_distance(current_position, self.goal_position)
        distance_to_start = get_distance(current_position, self.start_position)

        if self.finished:
            return

        print(f'distance to goal: {distance_to_goal}')
        print(f'distance to start: {distance_to_start}')

        if not self.started and distance_to_start > 0.5:
            self.started = True
            self.start_time = rospy.get_rostime().to_sec()
            print(f'competition started at: {self.start_time}')

        if self.started and distance_to_goal < 1.0:
            self.finished = True
            self.end_time = rospy.get_rostime().to_sec()
            duration = self.end_time - self.start_time
            print(f'The competition was completed in {duration} seconds')

    def run_node(self):
        rospy.init_node('competition_manager')
        rospy.Subscriber("carla/ego_vehicle/odometry", Odometry, self.callback)
        rospy.spin()


def main():
    print('Init competition_manager')
    competition_manager = CompetitionManagerNode()
    competition_manager.run_node()


if __name__ == '__main__':
    main()
