import sys  # used to exit the program immediately
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.chdir("pegglepy")

##### local imports #####
try:
    from local.config import *
    from local.misc import *

    # refer to the vectors.py module for information on these functions
    from local.vectors import Vector, subVectors
    from local.collision import isBallTouchingPeg, resolveCollision

    from local.ball import Ball
    from local.peg import Peg
    from local.bucket import Bucket
except ImportError as e:
    print("ERROR: Unable to import local modules, this is likely due to a missing file or folder. Please make sure to run the script from within the PegglePy directory.")
    print(str(e))
    print("Exiting...")
    sys.exit(1)

os.chdir("../")
import controller_templates
from gamestate import *
import math
import time

def getGameID(games_queue: list[tuple[controller_templates.Controller, int]], sub_index: int):
    #print(games_queue[0])
    return games_queue[0][0].ID + "_" + str(sub_index)

def executeGameQueue(games_queue: list[tuple[controller_templates.Controller, int]], options = {}):
    os.chdir("pegglepy")

    if "balls" in options.keys():
        base_balls = options["balls"]
    else: base_balls = 10

    ### testing stuff ###
    balls: list[Ball]
    balls = []
    balls.append(Ball(WIDTH/2, HEIGHT/25))
    ball = balls[0]

    # some extra global variable initialization stuff
    bucket = Bucket()
    score = 0
    score_this_turn = 0
    pegsHit = 0
    launchAim = Vector(0, 0)

    pegs: list[Peg]
    pegs, originPegs, orangeCount, levelFileName = loadDefaultLevel()
    originPegs = pegs.copy()
    pegs = createPegColors(pegs)

    orangeCount = 0
    for peg in pegs:
        if peg.color == "orange":
            orangeCount += 1

    # assign each peg a screen location, this is to better optimize collison detection (only check pegs on the same screen location as the ball)
    assignPegScreenLocation(pegs, segmentCount)

    ballsRemaining, powerUpActive, powerUpCount, pitch, pitchRaiseCount, ball, score, pegsHit, pegs, orangeCount, gameOver, alreadyPlayedOdeToJoy, frameRate, longShotBonus, staticImage = resetGame(
                balls, assignPegScreenLocation, createPegColors, bucket, pegs, originPegs)
    ballsRemaining = base_balls

    history = {}
    results = {}

    sub_index = 0
    game_id = getGameID(games_queue, sub_index)

    history[game_id] = []

    ##### main loop #####
    while len(games_queue) > 0:
        launch_button = True

        # feed the network all the info about the gamestate
        # return an angle and what position in its cycle it wants the bucket to be
        if not ball.isAlive:
            angle, bucket_pos = games_queue[0][0].getShot(GameState(pegs, ballsRemaining, score))
            launchAim = Vector(math.cos(angle),math. sin(angle))


        # if mouse clicked then trigger ball launch
        if launch_button and not ball.isAlive and len(balls) < 2:
            ball.isLaunch = True
            ball.isAlive = True

        # launch ball
        if ball.isLaunch and ball.isAlive:
            launchForce = subVectors(launchAim, ball.pos)
            launchForce.setMag(LAUNCH_FORCE)
            ball.applyForce(launchForce)
            ball.isLaunch = False
            shouldClear = True

        # update ball physics and pegs, additional game logic
        if ball.isAlive:
            ballScreenPosList = getBallScreenLocation(ball, segmentCount)
            ball_pos_1 = ballScreenPosList[0]
            if len(ballScreenPosList) > 1:
                ball_pos_2 = ballScreenPosList[1]
            else: ball_pos_2 = False

            #### collision ####
            for p in pegs:
                # ball physics and game logic
                if ball_pos_1 in p.pegScreenLocations or (ball_pos_2 and ball_pos_2 in p.pegScreenLocations):
                    if isBallTouchingPeg(p.pos.x, p.pos.y, p.radius, ball.pos.x, ball.pos.y, ball.radius):
                        # resolve the collision between the ball and peg
                        # use the c implementation of the collision check
                        ball = resolveCollision(ball, p)

                        # save the peg that was last hit, used for when the ball is stuck and for bonus points
                        ball.lastPegHit = p

                        # automatically remove pegs that a ball is stuck on
                        if autoRemovePegs:
                            p.ballStuckTimer.update()

                            # when timer has triggered, remove the last hit peg
                            if p.ballStuckTimer.isTriggered and ball.lastPegHit != None:
                                pegs.remove(ball.lastPegHit)  # remove the peg
                                ball.lastPegHit = None
                                p.ballStuckTimer.cancleTimer()

                            # if the velocity is less than 0.5 then it might be stuck, wait a few seconds and remove the peg its stuck on
                            if ball.vel.getMag() <= 0.5 and p.ballStuckTimer.isActive == False:
                                p.ballStuckTimer.setTimer(
                                    autoRemovePegsTimerValue)
                            elif ball.vel.getMag() > 0.5:
                                p.ballStuckTimer.cancleTimer()
                                ball.lastPegHit = None

                        # peg color update and powerup sounds
                        if not p.isHit:
                            p.isHit = True
                            pegsHit += 1
                            p.update_color()  # change the color to signify it has been hit
                            if p.color == "orange":
                                orangeCount -= 1
                            if p.isPowerUp:
                                powerUpCount += 1
                                powerUpActive = True
                            
                            # keep track of points earned
                            added_score = (p.points * getScoreMultiplier(orangeCount, pegsHit))
                            score_this_turn += added_score
                            score += added_score
            
            ball.update()

            # check if ball has hit the sides of the bucket
            collidedPeg = bucket.isBallCollidingWithBucketEdge(ball)
            if collidedPeg:
                # use the c implementation of the collision check
                ball = resolveCollision(ball, collidedPeg)
            
            # if ball went in the bucket
            if not ball.inBucket and bucket.isInBucket(ball.pos.x, ball.pos.y):
                ball.inBucket = True  # prevent the ball from triggering it multiple times
                ballsRemaining += 1
            

            # if active spooky powerup
            if powerUpActive:
                if ball.pos.y + ball.radius > HEIGHT:
                    ball.pos.y = 0 + ball.radius
                    ball.inBucket = False
                    powerUpCount -= 1
                    if powerUpCount < 1:
                        powerUpActive = False
        
        
        if not ball.isAlive:
            # reset everything and remove hit pegs
            if shouldClear:
                shouldClear = False
                balls.clear()  # clear all the balls
                # recreate the original ball
                balls.append(Ball(WIDTH/2, HEIGHT/25))
                ball = balls[0]
                ball.reset()
                done = False
                ballsRemaining -= 1

                history[game_id].append({
                    "launch_angle": launchAim.getAngleDeg(),
                    "pegs_hit_this_turn": pegsHit,
                    "orange_pegs_left": orangeCount,
                    "score_this_turn": score_this_turn,
                    "score": score,
                    "balls_left": ballsRemaining
                })
                score_this_turn = 0
                pegsHit = 0
                for _ in range(8):  # temporary fix to bug with pegs not being removed
                    for p in pegs:
                        if p.isHit:
                            pegs.remove(p)
            
            # check if their are any orange pegs or if the player has no balls (lol)
            if orangeCount == 0 or ballsRemaining < 1:
                peg_count = 0
                for peg in pegs:
                    peg_count += 1

                results[game_id] = {
                    "orange_pegs_left": orangeCount,
                    "pegs_left": peg_count,
                    "score": score,
                    "balls_left": ballsRemaining
                }

                sub_index += 1
                if sub_index >= games_queue[0][1]:
                    games_queue.pop(0)
                    sub_index = 0
                else:
                    # wipe anything relevant to this game from the controller's memory
                    games_queue[0][0].reset()
                if len(games_queue) > 0:
                    game_id = getGameID(games_queue, sub_index)
                    history[game_id] = []

                # reset the game
                ballsRemaining, powerUpActive, powerUpCount, pitch, pitchRaiseCount, ball, score, pegsHit, pegs, orangeCount, gameOver, alreadyPlayedOdeToJoy, frameRate, longShotBonus, staticImage = resetGame(
                    balls, assignPegScreenLocation, createPegColors, bucket, pegs, originPegs)
                ballsRemaining = base_balls

        # bucket, pass the power up info for the bucket to update its collison and image
        bucket.update(powerUpType, powerUpActive)
    pygame.quit()
    os.chdir("../")
    return (results, history)