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
os.chdir("pegglepy")

def getGameID(games_queue: list[tuple[controller_templates.Controller, int]], sub_index: int):
    #print(games_queue[0])
    return games_queue[0][0].ID + "_" + str(sub_index)

def executeGameQueue(games_queue: list[tuple[controller_templates.Controller, int]]):
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
    done = False
    launchAim = Vector(0, 0)
    longShotBonus = False

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
        for b in balls:
            if b.isAlive:
                ballScreenPosList = getBallScreenLocation(b, segmentCount)
                #### collision ####
                for p in pegs:
                    # ball physics and game logic
                    shouldCheckCollision = False
                    for ballScreenPos in ballScreenPosList:
                        for pegScreenLocation in p.pegScreenLocations:
                            if ballScreenPos == pegScreenLocation:
                                shouldCheckCollision = True

                    if shouldCheckCollision:
                        ballTouchingPeg = isBallTouchingPeg(
                            p.pos.x, p.pos.y, p.radius, b.pos.x, b.pos.y, b.radius)
                        if ballTouchingPeg:
                            # resolve the collision between the ball and peg
                            # use the c implementation of the collision check
                            b = resolveCollision(b, p)

                            # save the peg that was last hit, used for when the ball is stuck and for bonus points
                            b.lastPegHit = p

                            # automatically remove pegs that a ball is stuck on
                            if autoRemovePegs:
                                p.ballStuckTimer.update()

                                # when timer has triggered, remove the last hit peg
                                if p.ballStuckTimer.isTriggered and b.lastPegHit != None:
                                    pegs.remove(b.lastPegHit)  # remove the peg
                                    b.lastPegHit = None
                                    p.ballStuckTimer.cancleTimer()

                                # if the velocity is less than 0.5 then it might be stuck, wait a few seconds and remove the peg its stuck on
                                if b.vel.getMag() <= 0.5 and p.ballStuckTimer.isActive == False:
                                    p.ballStuckTimer.setTimer(
                                        autoRemovePegsTimerValue)
                                elif b.vel.getMag() > 0.5:
                                    p.ballStuckTimer.cancleTimer()
                                    b.lastPegHit = None

                            # check for long shot bonus
                            if b.lastPegHitPos != p.pos and b.lastPegHitPos != None and p.color == "orange" and not p.isHit:
                                if distBetweenTwoPoints(b.lastPegHitPos.x, b.lastPegHitPos.y, p.pos.x, p.pos.y) > longShotDistance:
                                    if not longShotBonus:
                                        score += 25000
                                        b.lastPegHitPos = None
                                        longShotBonus = True

                            # used for long shot check
                            b.lastPegHitPos = p.pos

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

                b.update()

                # check if ball has hit the sides of the bucket
                isBallCollidedBucket, collidedPeg = bucket.isBallCollidingWithBucketEdge(b)
                if isBallCollidedBucket:
                    # use the c implementation of the collision check
                    b = resolveCollision(b, collidedPeg)

                # if active spooky powerup
                if powerUpActive:
                    if b.pos.y + b.radius > HEIGHT:
                        b.pos.y = 0 + b.radius
                        b.inBucket = False
                        powerUpCount -= 1
                        if powerUpCount < 1:
                            powerUpActive = False

                # if ball went in the bucket
                if not b.inBucket and bucket.isInBucket(b.pos.x, b.pos.y):
                    b.inBucket = True  # prevent the ball from triggering it multiple times
                    ballsRemaining += 1

            # remove any 'dead' balls
            elif not b.isAlive and b != ball:
                balls.remove(b)

        # this little loop and if statement will determine if any of the balls are still alive and therfore if everything should be cleared/reset or not
        done = True
        for b in balls:
            if b.isAlive:
                done = False
                break

        if done:
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
                longShotBonus = False
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
                if len(games_queue) > 0:
                    game_id = getGameID(games_queue, sub_index)
                    history[game_id] = []

                # reset the game
                ballsRemaining, powerUpActive, powerUpCount, pitch, pitchRaiseCount, ball, score, pegsHit, pegs, orangeCount, gameOver, alreadyPlayedOdeToJoy, frameRate, longShotBonus, staticImage = resetGame(
                    balls, assignPegScreenLocation, createPegColors, bucket, pegs, originPegs)

        # bucket, pass the power up info for the bucket to update its collison and image
        bucket.update(powerUpType, powerUpActive)
    pygame.quit()
    return (results, history)