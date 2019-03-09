pragma solidity ^0.5.5;

contract DCCJobContract {
    struct Slave {
        bool exists;
        uint256 hash;
        string encodedBinary; // Base64 encoded
    }

    address payable public owner = msg.sender;
    bool public inProgress;
    string public srcCode;
    uint256 public price;
    uint32 public numSlavesMax;

    address payable[] slaveAddresses;
    mapping(address => Slave) slaves;

    event JobCompleted(uint256 hash, uint32[] goodSlaves);
    event JobFailed();

    constructor(string memory _srcCode, uint32 _numSlavesMax) payable public {
        require(msg.sender == owner);
        require(!inProgress);

        srcCode = _srcCode;
        inProgress = true;
        price = msg.value;
        numSlavesMax = _numSlavesMax;
    }

    function checkCompletion() private {
        require(slaveAddresses.length == numSlavesMax);

        uint256 maxFreq = 0;
        uint256 maxHash;
        for (uint32 i = 0; i < numSlavesMax; i++) {
            uint256 shash = slaves[slaveAddresses[i]].hash;
            uint32 matches = 0;
            for (uint32 j = 0; j < numSlavesMax; j++) {
                if (slaves[slaveAddresses[j]].hash == shash) {
                    matches++;
                }
            }

            if (matches > maxFreq) {
                maxFreq = matches;
                maxHash = shash;
            }
        }

        uint32 k1 = 0;
        uint32[] memory goodSlaves = new uint32[](slaveAddresses.length);
        for (uint32 i = 0; i < numSlavesMax; i++) {
            uint256 shash = slaves[slaveAddresses[i]].hash;
            if (shash == maxHash) {
                goodSlaves[k1] = i;
                k1++;
            }
        }

        if (10 * k1 < 9 * numSlavesMax) {
            owner.transfer(price);

            emit JobFailed();
            inProgress = false;
        } else {
            uint256 pricePer = price / k1;
            for (uint32 i = 0; i < k1; i++) {
                slaveAddresses[goodSlaves[i]].transfer(pricePer);
            }

            owner.transfer(address(this).balance);

            emit JobCompleted(slaves[slaveAddresses[goodSlaves[0]]].hash, goodSlaves);
            inProgress = false;
        }

        delete goodSlaves;
    }

    function submit(uint256 _hash, string calldata _encodedBinary) external {
        require(!slaves[msg.sender].exists);
        require(inProgress);
        require(msg.sender != owner);

        slaveAddresses.push(msg.sender);
        slaves[msg.sender] = Slave({ exists: true, hash: _hash, encodedBinary: _encodedBinary });

        if (slaveAddresses.length == numSlavesMax) {
            checkCompletion();
        }
    }
}
