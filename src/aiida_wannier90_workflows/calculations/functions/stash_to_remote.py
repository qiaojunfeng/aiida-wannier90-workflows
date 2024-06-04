"""Calcfunction for RemoteStashFolderData."""

from aiida import orm
from aiida.engine import calcfunction


@calcfunction
def stash_to_remote(
    stash_data: orm.RemoteStashFolderData, computer_label: orm.Str = None
) -> orm.RemoteData:
    """Convert a ``RemoteStashFolderData`` into a ``RemoteData`` on a different computer.

    Note although the new ``computer`` is different from the old one, actually they should be the same
    physical machine and the `path` must be accessible for both ``computer``s. This is a convenience
    wrapper for restarting from charge density, and submit new jobs on a different partition or
    with different slurm account.

    Reason to add this ``calcfunction``:
    The imported ``RemoteData`` cannot be used for restarting Wannier90BandsWorkChain, due to the error
    'Remote copy between two different machines is not implemented yet'.
    This function create a new ``RemoteData`` with the same path as the imported ``RemoteData``, but with
    a different ``computer``, thus allowing restart from the remote charge density.

    Note that for ``computer_label`` I use ``orm.Str`` instead of ``orm.Computer``,
    since I cannot pass ``orm.Computer`` to ``calcfunction``:
        ValueError: Error occurred validating port 'inputs.computer': value 'computer' is not of the right type.
    """
    if computer_label is None:
        computer = stash_data.computer
    else:
        computer = orm.load_computer(computer_label.value)

    if stash_data.get_attribute("stash_mode") != "copy":
        raise NotImplementedError("Only the `copy` stash mode is supported.")

    remote_data = orm.RemoteData()
    remote_data.set_remote_path(stash_data.get_attribute("target_basepath"))
    remote_data.computer = computer

    return remote_data
