pragma solidity ^0.8.0;

import "./Tornado.sol";
import "./IERC20.sol";
import "./SafeERC20.sol";
import "./MerkleTreeWithHistory.sol";

contract example is Tornado{
    uint256 red=0;
    uint256 blue=0;
    using SafeERC20 for IERC20;
    IERC20 public token;
    address admin;
    constructor(
    IVerifier _verifier,
    IHasher _hasher,
    uint256 _denomination,
    uint32 _merkleTreeHeight,
    IERC20 _token,
    address _address
  ) Tornado(_verifier, _hasher, _denomination, _merkleTreeHeight) {
    token = _token;
    admin=_address;
  }

  function _processDeposit() internal override {
    require(msg.value == 0, "ETH value is supposed to be 0 for ERC20 instance");
    token.safeTransferFrom(msg.sender, address(this), denomination);
  }

  function _processWithdraw(
    address payable _recipient,
    address payable _relayer,
    uint256 _fee,
    uint256 _refund
  ) internal override {
    require(msg.value == _refund, "Incorrect refund amount received by the contract");

        token.safeTransfer(_recipient, denomination - _fee);
        if (_fee > 0) {
          token.safeTransfer(_relayer, _fee);
        }

        if (_refund > 0) {
          (bool success, ) = _recipient.call{ value: _refund }("");
          if (!success) {
            // let's return _refund back to the relayer
            _relayer.transfer(_refund);
          }
        }
      }


    function vote(bytes32 _hash) public payable{
      super.deposit(_hash);
    }
    
    function withdraw(bytes calldata _proof1, bytes calldata _proof2,
    bytes32 _root,
    bytes32 _nullifierHash,
    address payable _recipient,
    address payable _relayer,
    uint256 _fee,
    uint256 _refund) public payable{

      require(msg.sender==admin, "This function can only be called by admin");

      if(verifier.verifyProof(_proof1,[uint256(_root), uint256(_nullifierHash), f(_recipient), f(_relayer), _fee, _refund])==true){
        red++;
        super.withdraw( _proof1, _root, _nullifierHash, _recipient, _relayer, _fee, _refund);
      }
      if(verifier.verifyProof(_proof2,[uint256(_root), uint256(_nullifierHash), f(_recipient), f(_relayer), _fee, _refund])==true){
        blue++;
        super.withdraw( _proof2, _root, _nullifierHash, _recipient, _relayer, _fee, _refund);
      }
    }

}